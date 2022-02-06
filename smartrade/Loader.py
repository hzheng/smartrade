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
        db = self._db
        if reload:
            db.transactions.drop()
        for tx in transactions:
            symbol = tx.symbol
            transaction = {
                'date': tx.date,
                'action': str(tx.action).split('.')[1],
                'quantity': tx.quantity,
                'price': tx.price,
                'fee': tx.fee,
                'amount': tx.amount,
                'type': str(symbol.type).split('.')[1],
                'description': tx.description
            }
            if symbol.ui:
                transaction['ui'] = symbol.ui
                if symbol.strike:
                    transaction['strike'] = symbol.strike
                    transaction['expired'] = symbol.expired

            db.transactions.insert_one(transaction)