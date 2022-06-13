# -*- coding: utf-8 -*-

from typing import Iterable, Union

from datetime import datetime, time, timedelta, timezone

from dateutil.parser import parse

from smartrade import app_logger
from smartrade.BrokerClient import BrokerClient
from smartrade.MarketApi import MarketApi
from smartrade.utils import get_database, ASC, DESC

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
    def _day_range(cls, day, min_time=None, max_time=None):
        min_date = datetime.combine(day.date(), min_time or datetime.min.time())
        max_date = datetime.combine(day.date(), max_time or datetime.max.time())
        return {'date': {'$gte': min_date, '$lte': max_date}}

    def _get_quotes(self, symbols, day, min_time=None, max_time=None):
        return self._quote_collection.find({**self._day_range(day, min_time, max_time),
                                            'symbol': {'$in': symbols}}).limit(1)

    def get_quotes(self, symbols : Union[str, Iterable[str]], day=None):
        '''
        day: date of quotes, default: today's date
        '''
        if isinstance(symbols, str):
            symbols = [symbols]
        elif not isinstance(symbols, list):
            symbols = list(symbols)

        time_zone = timezone.utc
        now = datetime.now(time_zone)
        current_trading_time = self._trading_day(now)
        market_open_time = datetime.combine(current_trading_time, self.OPEN_TIME).replace(tzinfo=time_zone)
        market_close_time = datetime.combine(current_trading_time, self.CLOSE_TIME).replace(tzinfo=time_zone)
        logger.debug("open time: %s, close time: %s", market_open_time, market_close_time)
        if not day:
            day = now
        elif isinstance(day, str):
            day = parse(day).replace(tzinfo=time_zone)
        elif isinstance(day, datetime):
            day = day.replace(tzinfo=time_zone)
        logger.debug("get quotes for %s at the day: %s", symbols, day)
        res = None
        if market_open_time <= day <= market_close_time:
            logger.debug("market is open.")
        else:
            day = datetime.combine(self._trading_day(day).date(), self.CLOSE_TIME)
            logger.debug("market is closed, check if we already have record for day: %s", day)
            res = [doc for doc in self._get_quotes(symbols, day, self.CLOSE_TIME)]
            if len(res) == len(symbols):
                logger.debug("we already have all data")
            else:
                logger.debug("we don't have all data")
                res = None
        if not res and self._retrieve_and_save(symbols, day):
            res = self._get_quotes(symbols, day)
        if res:
            return {doc['symbol']: ((doc['bidPrice'] + doc['askPrice']) / 2,
                                    doc['netChange'],
                                    # doc['markChangeInDouble'],
                                    doc.get('netPercentChangeInDouble', 0)
                                    ) for doc in res}
                
        logger.warning("resort to old quote for %s", symbols)
        quotes = {}
        for symbol in symbols:
            for doc in self._quote_collection.find({'date': {'$lte': day}, 'symbol': symbol}).sort(
                [("date", DESC)]).limit(1):
                quotes[symbol]=(doc['bidPrice'] + doc['askPrice']) / 2
        return quotes

    def _retrieve_and_save(self, symbols, day):
        logger.debug("retrieving quote at date %s...", day)
        try:
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
            return True
        except Exception as e:
            # logger.error("Error occurred", exc_info=True)
            logger.error("failed to quota occurred: %s", e)

    def get_daily_price_history(self, symbol, start_date=None, end_date=None):
        '''
        Retrieve daily price history as late as yesterday.

        start_date: date in UTC timezone, default: earliest yesterday
        end_date: date in UTC timezone, default: latest yesterday
        '''
        today = datetime.utcnow().date()
        earliest_today = datetime.combine(today, datetime.min.time())
        latest_yesterday = earliest_today - timedelta(milliseconds=1)
        if not end_date or end_date > latest_yesterday:
            end_date = latest_yesterday
        if not start_date:
            start_date = earliest_today - timedelta(days=1)
        if start_date > end_date: return []

        next_saved_time = None
        for doc in self._price_collection.find({'symbol': symbol}).sort([("time", DESC)]).limit(1):
            next_saved_time = doc['time'] + timedelta(days=1)
        if next_saved_time and next_saved_time >= end_date:
            logger.info(f"all prices of {symbol} were retrieved before")
        elif next_saved_time:
            logger.info(f"part of prices of {symbol} were retrieved before")
            self._retrieve_and_save_daily_prices(symbol, next_saved_time, latest_yesterday, True)
        else:
            logger.info(f"price of {symbol} is never retrieved before")
            self._retrieve_and_save_daily_prices(symbol, earliest_today - timedelta(days=365*20), latest_yesterday, False)

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
        today = datetime.now().date()
        earliest_today = datetime.combine(today, datetime.min.time())
        latest_yesterday = earliest_today - timedelta(milliseconds=1)
        if not day or day > latest_yesterday:
            day = datetime.now()
        prices = self.get_quotes(symbol, day).get(symbol, None)
        price = prices[0] if prices else 0
        if price > 0 or not day: return price

        logger.warning("cannot find the quote of symbol %s", symbol)
        # fallback: price history
        start_date = day - timedelta(days=10)
        end_date = datetime.combine(day.date(), datetime.max.time())
        prices = self.get_daily_price_history(symbol, start_date, end_date)
        #return prices[-1]['weighted_average'] if prices else 0
        return prices[-1]['close'] if prices else 0