# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

from pymongo import MongoClient

class Inspector:
    def __init__(self, db_name):
        client = MongoClient()
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

    def distinct_ticks(self):
        return self._transactions.distinct('ui')

    def tick_transactions(self, tick):
        transactions = []
        for doc in self._transactions.find({'ui': tick}):
            transaction = Transaction.from_doc(doc)
            transactions.append(transaction)
        return transactions

    def tick_costs(self, tick):
        amount = 'total_amount'
        res = self._transactions.aggregate(
            [{'$match': {'ui': tick}},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0
