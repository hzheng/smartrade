# -*- coding: utf-8 -*-

from typing import Iterable, Union

from datetime import datetime, time, timedelta, timezone
from time import sleep

from dateutil.parser import parse

from smartrade import app_logger
from smartrade.BrokerClient import BrokerClient
from smartrade.MarketApi import MarketApi
from smartrade.Transaction import Symbol
from smartrade.exceptions import TooManyRequestsError
from smartrade.utils import check, get_database, ASC, DESC

logger = app_logger.get_logger(__name__)

class MarketDataProvider:
    OPEN_TIME = time(13, 30)
    CLOSE_TIME = time(20)

    def __init__(self, broker: BrokerClient, market_api: MarketApi, db_name: str):
        self._broker = broker
        self._api = market_api
        db = get_database(db_name)
        self._quote_collection = db.quotes
        self._price_collection = db.price_history

    @classmethod
    def _trading_day(cls, day):
        weekday = day.weekday()
        if 0 <= weekday < 5: return day

        return day - timedelta((weekday + 3) % 7)

    @classmethod
    def _trading_time(cls, day, time_zone=timezone.utc):
        trading_day = cls._trading_day(day)
        open_time = datetime.combine(trading_day, cls.OPEN_TIME).replace(tzinfo=time_zone)
        if trading_day < open_time:
            trading_day = cls._trading_day(trading_day - timedelta(days=1))
            open_time = datetime.combine(trading_day, cls.OPEN_TIME).replace(tzinfo=time_zone)
        close_time = datetime.combine(trading_day, cls.CLOSE_TIME).replace(tzinfo=time_zone)
        return (open_time, close_time)

    @classmethod
    def _day_range(cls, day, min_time=None, max_time=None):
        min_date = datetime.combine(day.date(), min_time or datetime.min.time())
        max_date = datetime.combine(day.date(), max_time or datetime.max.time())
        return {'date': {'$gte': min_date, '$lte': max_date}}

    def _get_quotes(self, symbols, day, min_time=None, max_time=None):
        return self._quote_collection.find({**self._day_range(day, min_time, max_time),
                                            'symbol': {'$in': symbols}})

    def get_quotes(self, symbols : Union[str, Iterable[str]], day=None):
        '''
        Args:
            symbols: (list of) symbol(s) to be quoted
            day: date of quotes, default: today's date
        Returns:
            (quote dict, real quote)
        '''
        if isinstance(symbols, str):
            symbols = [symbols]
        elif not isinstance(symbols, list):
            symbols = list(symbols)

        time_zone = timezone.utc
        now = datetime.now(time_zone)
        market_open_time, market_close_time = self._trading_time(now)
        logger.debug("open time: %s, close time: %s", market_open_time, market_close_time)
        market_hours = self.get_market_hours(now)
        if market_hours:
            if False: # TODO: may differ due to time zone
                check(market_hours[0] == market_open_time, f"{market_hours[0]} should equal to {market_open_time}")
                check(market_hours[1] == market_close_time, f"{market_hours[1]} should equal to {market_close_time}")
        else: # weekend, holiday or any day before today
            logger.info("market hours is unavailable") # TODO: check a non-weekend holiday
        if not day:
            day = now
        elif isinstance(day, str):
            day = parse(day).replace(tzinfo=time_zone)
        elif isinstance(day, datetime):
            day = day.replace(tzinfo=time_zone)
        logger.debug("get quotes for %s at the day: %s", symbols, day)
        res = None
        if market_open_time <= day < market_close_time:
            logger.debug("market is open at the time: %s", day)
        else:
            close_time = self._trading_time(day)[1]
            logger.debug("market is closed, check if we already have record for day: %s", close_time)
            res = [doc for doc in self._get_quotes(symbols, close_time, self.CLOSE_TIME)]
            if len(res) == len(symbols):
                logger.debug("we already have all data")
            else:
                logger.debug("we don't have all data")
                res = None
        quote_time = min(day, market_close_time)
        if not res and day >= market_open_time and self._retrieve_and_save(symbols, quote_time):
            res = self._get_quotes(symbols, quote_time)
        if res:
            return {doc['symbol']: self._quote_info(doc) for doc in res}, True
 
        logger.warning("resort to old quote for %s", symbols)
        quotes = {}
        for symbol in symbols:
            for doc in self._quote_collection.find({'date': {'$lte': day}, 'symbol': symbol}).sort(
                [("date", DESC)]).limit(1):
                quotes[symbol] = self._quote_info(doc)
        return quotes, False
    
    def _quote_info(self, doc):
        return ((doc['bidPrice'] + doc['askPrice']) / 2,
                doc['netChange'],
                # doc['markChangeInDouble'],
                doc.get('netPercentChangeInDouble', 0)
                )

    def _retrieve_and_save(self, symbols, day):
        while True:
            try:
                logger.debug("retrieving quote(latest market price) of %s at time %s...", symbols, day)
                self._do_retrieve_and_save(symbols, day)
                return True
            except TooManyRequestsError:
                logger.warn("Too many requests, retry after 30 seconds...")
                sleep(30)
            except Exception as e:
                # logger.error("Error occurred", exc_info=True)
                logger.error("failed to quote (error type: %s, error: %s)", type(e), e)
                return False

    def _do_retrieve_and_save(self, symbols, day):
        quotes = self._broker.get_quotes(symbols)
        for symbol, quote in quotes.items():
            specifier = {**self._day_range(day), 'symbol': symbol}
            q = {'symbol': symbol, 'date': day}
            for key in ('bidPrice', 'askPrice', 'lastPrice', 'openPrice',
                        'highPrice', 'lowPrice', 'closePrice', 'netChange',
                        'markPercentChangeInDouble', 'markChangeInDouble',
                        'netPercentChangeInDouble', 'volatility',
                        'bidSize', 'askSize', 'lastSize', 'totalVolume', 'mark'):
                q[key] = quote[key]
            if '_' in symbol:
                for key in ('delta', 'gamma', 'theta', 'vega', 'rho',
                            'openInterest',  'moneyIntrinsicValue', 
                            'timeValue', 'theoreticalOptionValue', 'impliedYield'):
                    q[key] = quote[key]
            else:
                for key in ('52WkHigh', '52WkLow',  'peRatio'):
                    q[key] = quote[key]
            self._quote_collection.replace_one(specifier, q, upsert=True)

    def get_daily_price_history(self, symbol, start_date=None, end_date=None):
        '''
        Retrieve daily price history as late as yesterday or expiration day.

        start_date: date in UTC timezone, default: earliest yesterday
        end_date: date in UTC timezone, default: latest yesterday
        '''
        today = datetime.utcnow().date()
        time_zone = timezone.utc
        earliest_today = datetime.combine(today, datetime.min.time()).replace(tzinfo=time_zone)
        latest_day = earliest_today - timedelta(milliseconds=1)
        symbol_obj = Symbol(symbol)
        if symbol_obj.is_option():
            latest_day = min(latest_day, datetime.combine(symbol_obj.expired, datetime.min.time()).replace(tzinfo=time_zone))
            #TODO: option price may not available when it's 0
        if not end_date or end_date > latest_day:
            end_date = latest_day

        if not start_date:
            start_date = earliest_today - timedelta(days=1)
        if start_date > end_date: return []

        next_saved_time = None
        for doc in self._price_collection.find({'symbol': symbol}).sort([("time", DESC)]).limit(1):
            next_saved_time = doc['time'].replace(tzinfo=time_zone) + timedelta(days=1)
        logger.debug(f"next_save_time: {next_saved_time}, end_date: {end_date}")
        if next_saved_time and next_saved_time >= end_date:
            logger.info(f"all prices of {symbol} were retrieved before")
        elif next_saved_time:
            logger.info(f"part of prices of {symbol} were retrieved before")
            self._retrieve_and_save_daily_prices(symbol, next_saved_time, latest_day, True)
        else:
            logger.info(f"price of {symbol} is never retrieved before")
            self._retrieve_and_save_daily_prices(symbol, earliest_today - timedelta(days=365*20), latest_day, False)

        res = self._price_collection.find(
            {'symbol': symbol, 'time': {'$gte': start_date, '$lte': end_date}}).sort([("time", ASC)])
        return [doc for doc in res]
    
    def _retrieve_and_save_daily_prices(self, symbol, start_date, end_date, short_term):
        logger.info(f"Retrieving price history of {symbol} from {start_date} to {end_date}...")
        if '_' in symbol or short_term: # delta < 365 * 2:
            # free polygon api only support 2-year history
            res = self._api.get_daily_prices(symbol, start_date, end_date)
        else:
            # TDAmeritrade doesn't support option and some stock data(e.g. HOOD) sometimes are unavailable
            res = self._broker.get_daily_prices(symbol, start_date, end_date)
        for doc in res:
            doc['symbol'] = symbol
            specifier = {'time': doc['time'], 'symbol': symbol}
            self._price_collection.replace_one(specifier, doc, upsert=True)

    def get_price(self, symbol, day : datetime = None):
        '''
        day: date of price, default: today's date
        '''
        time_zone = timezone.utc
        if day:
            day = day.replace(tzinfo=time_zone)
        logger.debug("getting price of %s on %s", symbol, day)
        now = datetime.now(time_zone)
        today = now.date()
        earliest_today = datetime.combine(today, datetime.min.time()).replace(tzinfo=time_zone)
        latest_yesterday = earliest_today - timedelta(milliseconds=1)
        if not day or day > latest_yesterday:
            day = now
        prices, actual = self.get_quotes(symbol, day)
        if actual:
            price = prices.get(symbol, None)
            if price: return price[0]

        logger.warning("cannot find the quote of symbol %s", symbol)
        # fallback: price history
        start_date = day - timedelta(days=10)
        end_date = datetime.combine(day.date(), datetime.max.time()).replace(tzinfo=time_zone)
        prices = self.get_daily_price_history(symbol, start_date, end_date)
        #return prices[-1]['weighted_average'] if prices else 0
        return prices[-1]['close'] if prices else 0
    
    def get_market_hours(self, day=None):
        if not day:
            day = datetime.now()
        elif isinstance(day, str):
            day = parse(day)
        hours = self._broker.get_market_hours(day)
        if not hours:
            return None
        
        start, end = hours
        return parse(start), parse(end)
