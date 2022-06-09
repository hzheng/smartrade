# -*- coding: utf-8 -*-

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

    def get_quotes(self, symbols, day=None):
        '''
        day: date in UTC timezone, default: today's date
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
            day = parse(day)
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
                                    doc['netChange'], #doc['markChangeInDouble'],
                                    doc['netPercentChangeInDouble']) for doc in res}
                
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

    def get_daily_prices(self, symbol, start_date=None, end_date=None):
        now = datetime.now()
        if not start_date:
            start_date = now - timedelta(days=1)
        if not end_date:
            end_date = now + timedelta(days=1)
        delta = (now - start_date).days
        if '_' in symbol or delta < 365 * 2:
            # api only support 2-year history
            return self._api.get_daily_prices(symbol, start_date, end_date)
        # broker doesn't support option and some stock data(e.g. HOOD) are unavailable
        return self._broker.get_daily_prices(symbol, start_date, end_date)
