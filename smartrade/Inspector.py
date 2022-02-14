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

    def distinct_ticks(self, to_date=None):
        condition = {}
        if to_date:
            condition['date'] = {"$lte": to_date}
        return self._transactions.distinct('ui', condition)

    def tick_transactions(self, tick):
        transactions = []
        for doc in self._transactions.find({'ui': tick}):
            transaction = Transaction.from_doc(doc)
            transactions.append(transaction)
        return transactions

    def tick_costs(self, tick, to_date=None):
        amount = 'total_amount'
        condition = {'ui': tick}
        if to_date:
            condition['date'] = {"$lte": to_date}
        res = self._transactions.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0