# -*- coding: utf-8 -*-

from datetime import date, datetime

from dateutil.parser import parse
import pymongo

from smartrade.BrokerClient import BrokerClient


class MarketDataProvider:
    def __init__(self, broker: BrokerClient, db_name: str):
        self._broker = broker
        mongo_client = pymongo.MongoClient()
        self._db = mongo_client[db_name]
        self._quote_collection = self._db.quotes

    def get_quotes(self, symbols, day=None):
        today = datetime.combine(date.today(), datetime.min.time())
        if not day:
            day = today
        elif isinstance(day, str):
            day = parse(day)
        if day >= today:
            self._save(symbols, today)
        if isinstance(symbols, str):
            symbols = [symbols]
        elif not isinstance(symbols, list):
            symbols = list(symbols)
        res = self._quote_collection.find({'date': day, 'symbol': {'$in': symbols}})
        return {doc['symbol']: (doc['bidPrice'] + doc['askPrice']) / 2 for doc in res}

    def _save(self, symbols, today):
        quotes = self._broker.get_quotes(symbols)
        for symbol, quote in quotes.items():
            specifier = {'symbol': symbol, 'date': today}
            q = {**specifier}
            for key in ('bidPrice', 'askPrice', 'lastPrice', 'openPrice',
                        'highPrice', 'lowPrice', 'closePrice', 'netChange'):
                q[key] = quote[key]
            if '_' in symbol:
                for key in ('delta', 'gamma', 'theta', 'vega', 'rho', 'volatility'):
                    q[key] = quote[key]
            self._quote_collection.replace_one(specifier, q, upsert=True)