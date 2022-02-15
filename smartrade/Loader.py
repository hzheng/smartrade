# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

from pymongo import MongoClient

import csv

class Loader:
    def __init__(self, db_name, format='schwab'):
        client = MongoClient()
        self._db = client[db_name]
        self._format = format

    def load(self, filename, reload=True):
        valid_transactions, invalid_transactions = self._parse_csv(filename)
        self._save(valid_transactions, reload)
        return valid_transactions, invalid_transactions

    def _parse_csv(self, path):
        valid_transactions = []
        invalid_transactions = []
        with open(path) as csvfile:
            for row in csv.reader(csvfile):
                try:
                    date, action, symbol, description, quantity, price, fee, amount, _ = row
                    tx = Transaction.from_dict(date=date, action=action, symbol=symbol, quantity=quantity, price=price, fee=fee, amount=amount, description=description)
                    if tx.is_valid():
                        valid_transactions.append(tx)
                    else:
                        invalid_transactions.append(tx)
                except Exception as e:
                    print(e)
                    continue
        return valid_transactions, invalid_transactions

    def _save(self, transactions, reload):
        tx_db = self._db.transactions
        if reload:
            tx_db.drop()
        for tx in transactions:
            tx_db.insert_one(tx.to_json())
