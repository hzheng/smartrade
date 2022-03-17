# -*- coding: utf-8 -*-

from calendar import weekday
from datetime import date, datetime, timedelta

from dateutil.parser import parse
import pymongo

from smartrade import app_logger
from smartrade.BrokerClient import BrokerClient

logger = app_logger.get_logger(__name__)

class MarketDataProvider:
    def __init__(self, broker: BrokerClient, db_name: str):
        self._broker = broker
        mongo_client = pymongo.MongoClient()
        self._db = mongo_client[db_name]
        self._quote_collection = self._db.quotes

    @classmethod
    def _trading_day(cls, day):
        weekday = day.weekday()
        if 1 <= weekday <= 5: return day

        return day - timedelta((weekday + 2) % 7)

    def get_quotes(self, symbols, day=None):
        today = self._trading_day(datetime.combine(date.today(), datetime.min.time()))
        if not day:
            day = today
        elif isinstance(day, str):
            day = parse(day)
        logger.debug("get quotes for %s at the day: %s", symbols, day)
        day = self._trading_day(day)
        has_latest_quote = True
        if day >= today:
            has_latest_quote = self._retrieve_and_save(symbols, today)
        if isinstance(symbols, str):
            symbols = [symbols]
        elif not isinstance(symbols, list):
            symbols = list(symbols)
        if has_latest_quote:
            res = self._quote_collection.find({'date': day, 'symbol': {'$in': symbols}})
            return {doc['symbol']: ((doc['bidPrice'] + doc['askPrice']) / 2,
                                    doc['markChangeInDouble'],
                                    doc['netPercentChangeInDouble']) for doc in res}
        
        logger.warning("resort to old quote for %s", symbols)
        quotes = {}
        for symbol in symbols:
            for doc in self._quote_collection.find({'date': {'$lte': day}, 'symbol': symbol}).sort(
                [("date", pymongo.DESCENDING)]).limit(1):
                quotes[symbol]=(doc['bidPrice'] + doc['askPrice']) / 2
        return quotes

    def _retrieve_and_save(self, symbols, today):
        try:
            quotes = self._broker.get_quotes(symbols)
            for symbol, quote in quotes.items():
                specifier = {'symbol': symbol, 'date': today}
                q = {**specifier}
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

