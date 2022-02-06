# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

from pymongo import MongoClient

class Inspector:
    def __init__(self, db_name):
        client = MongoClient()
        self._db = client[db_name]
        self._transactions = self._db.transactions

    def query_tick(self, tick):
        transactions = []
        for doc in self._transactions.find({'ui': tick}):
            transaction = Transaction.from_doc(doc)
            transactions.append(transaction)
        return transactions