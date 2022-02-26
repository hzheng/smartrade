# -*- coding: utf-8 -*-

import csv
import datetime
import json

from dateutil.parser import parse
import pymongo

from smartrade.Transaction import Transaction


class Loader:
    def __init__(self, db_name, broker=None):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._broker = broker
    
    def live_load(self, account_alias=None, start_date=None, end_date=None):
        if not start_date:
            for obj in self._db.transactions.find().sort([("date", pymongo.DESCENDING)]).limit(1):
                start_date = obj['date'] + datetime.timedelta(1)
        json_obj = self._broker.get_transactions(account_alias, start_date, end_date)
        valid_transactions, invalid_transactions = self._get_transactions(json_obj)
        self._save(valid_transactions, False)
        return valid_transactions, invalid_transactions

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
        with open(path) as json_file:
            return self._get_transactions(json.load(json_file))

    def _get_transactions(self, json_obj):
        valid_transactions = []
        invalid_transactions = []
        for obj in json_obj:
            description = obj['description'].upper()
            if description == "CASH ALTERNATIVES PURCHASE" or description.startswith("IGNORE"):
                continue

            tx_item = obj['transactionItem']
            date = obj['transactionDate']
            amount = obj.get('netAmount', None)
            quantity = tx_item.get('amount', None)
            price = tx_item.get('price', 0)
            total_fee = 0
            fees = obj['fees']
            for fee in fees.values():
                total_fee += fee
            total_fee -= min(fees['optRegFee'], fees['regFee']) #?
            total_fee -= fees['secFee'] # ?

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
            elif instruction is None:
                # invalid_transactions.append(obj)
                continue
            else:
                raise ValueError(f"unexpected instruction: {instruction}")

            symbol = self._get_symbol(instrument)
            if not symbol:
                invalid_transactions.append(obj)
                continue

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

    @classmethod
    def _get_symbol(cls, instrument):
        symbol = instrument.get('symbol', None)
        if symbol: return symbol

        exp_date = instrument.get('optionExpirationDate', None)
        if not exp_date: return

        exp_date = datetime.datetime.strptime(exp_date[:10], "%Y-%m-%d")
        cusip = instrument['cusip']
        # format 0SOXL.NI20041000
        parts = cusip.split(".")
        ui = parts[0][1:]
        strike = int(parts[-1][4:]) / 1000
        symbol = f"{ui} {exp_date.strftime('%m/%d/%Y')} {strike:.2f} P"
        return symbol
