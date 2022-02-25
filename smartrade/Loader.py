# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

from pymongo import MongoClient

import csv
import json

class Loader:
    def __init__(self, db_name):
        client = MongoClient()
        self._db = client[db_name]

    def load(self, path, reload=True):
        valid_transactions, invalid_transactions = self._parse_file(path)
        self._save(valid_transactions, reload)
        return valid_transactions, invalid_transactions

    def _parse_file(self, path):
        if path.endswith(".csv"): # schwab format
            return self._parse_csv(path)
        if path.endswith(".json"): # tdameritrade format
            return self._parse_json(path)

    def _parse_csv(self, path):
        valid_transactions = []
        invalid_transactions = []
        with open(path) as csv_file:
            for row in csv.reader(csv_file):
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

    def _parse_json(self, path):
        valid_transactions = []
        invalid_transactions = []
        with open(path) as json_file:
            for obj in json.load(json_file):
                description = obj['description'].upper()
                if description == "CASH ALTERNATIVES PURCHASE": continue

                tx_item = obj['transactionItem']
                date = obj['transactionDate']
                amount = obj.get('netAmount', None)
                quantity = tx_item.get('amount', None)
                price = tx_item.get('price', None)
                total_fee = 0
                fees = obj['fees']
                for fee in fees.values():
                    total_fee += fee
                if fees['optRegFee']: # ?
                    total_fee -= fees['regFee']

                instrument = tx_item.get('instrument', {})
                instruction = tx_item.get('instruction', None)
                position_effect = tx_item.get('positionEffect', None)

                if description.startswith("REMOVAL OF OPTION"):
                    if "ASSIGNMENT" in description:
                        action = "ASSIGNED"
                    elif "EXPIRATION" in description:
                        action = "EXPIRED"
                    else:
                        raise ValueError(f"unexpected description: {description}")
                elif instruction == 'BUY':
                    if position_effect == 'OPENING' or position_effect is None:
                        action = "BTO"
                    elif position_effect == 'CLOSING':
                        action = "BTC"
                    elif position_effect == 'AUTOMATIC':
                        action = "BTC" # ?
                    else:
                        raise ValueError(f"unexpected position_effect: {position_effect}")
                elif instruction == 'SELL':
                    if position_effect == 'OPENING':
                        action = "STO"
                    elif position_effect == 'CLOSING':
                        action = "STC"
                    elif position_effect == 'AUTOMATIC' or position_effect is None:
                        action = "STC" # ?
                    else:
                        raise ValueError(f"unexpected position_effect: {position_effect}")
                else:
                    raise ValueError(f"unexpected instruction: {instruction}")

                symbol = instrument.get('symbol', None)
                if symbol:
                    parts = symbol.split("_")
                    if len(parts) == 2:
                        tick, options = parts
                        exp_date = options[:2] + "/" + options[2:4] + "/20" + options[4:6]
                        symbol = f"{tick} {exp_date} {options[7:]} {options[6]}"

                tx = Transaction.from_dict(date=date, action=action, symbol=symbol, quantity=quantity, price=price, fee=total_fee, amount=amount, description=description)
                if tx.is_valid():
                    valid_transactions.append(tx)
                else:
                    invalid_transactions.append(tx)
        return valid_transactions, invalid_transactions

    def _save(self, transactions, reload):
        db = self._db
        if reload:
            db.client.drop_database(db.name)
        for tx in transactions:
            db.transactions.insert_one(tx.to_json())
