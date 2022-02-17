# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction
from smartrade.TransactionGroup import TransactionGroup

import pymongo

class Inspector:
    def __init__(self, db_name):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._tx_collection = self._db.transactions
        self._group_collection = self._db.transaction_groups

    def total_cash(self, to_date=None):
        amount = 'total_amount'
        condition = {}
        if to_date:
            condition['date'] = {"$lte": to_date}
        res = self._tx_collection.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def distinct_tickers(self, to_date=None):
        condition = {}
        if to_date:
            condition['date'] = {"$lte": to_date}
        return self._tx_collection.distinct('ui', condition)

    def ticker_costs(self, ticker, to_date=None):
        amount = 'total_amount'
        condition = {'ui': ticker}
        if to_date:
            condition['date'] = {"$lte": to_date}
        res = self._tx_collection.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def ticker_transactions(self, ticker):
        return [Transaction.from_doc(doc) for doc in self._tx_collection.find({'ui': ticker})]
    
    def ticker_transaction_groups(self, ticker):
        return [TransactionGroup.from_doc(doc) for doc in self._group_collection.find({'ui': ticker})]
