# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

import pymongo

class Inspector:
    def __init__(self, db_name):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._transactions = self._db.transactions

    def total_cash(self, to_date=None):
        amount = 'total_amount'
        condition = {}
        if to_date:
            condition['date'] = {"$lte": to_date}
        res = self._transactions.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def distinct_tickers(self, to_date=None):
        condition = {}
        if to_date:
            condition['date'] = {"$lte": to_date}
        return self._transactions.distinct('ui', condition)

    def ticker_transactions(self, ticker):
        transactions = []
        for doc in self._transactions.find({'ui': ticker}):
            transaction = Transaction.from_doc(doc)
            transactions.append(transaction)
        return transactions

    def ticker_costs(self, ticker, to_date=None):
        amount = 'total_amount'
        condition = {'ui': ticker}
        if to_date:
            condition['date'] = {"$lte": to_date}
        res = self._transactions.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0