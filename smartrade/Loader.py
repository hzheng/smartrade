# -*- coding: utf-8 -*-

import csv
import datetime
import json
import re

import pymongo

from smartrade import app_logger
from smartrade.Transaction import Transaction

logger = app_logger.get_logger(__name__)

class Loader:
    def __init__(self, db_name, account, broker=None):
        client = pymongo.MongoClient()
        db = client[db_name]
        self._transactions = db.transactions
        self._transaction_groups = db.transaction_groups
        self._account = account[-4:]
        self._account_cond = {'account' : account[-4:]}
        self._valid_tx_cond = {**self._account_cond, 'valid': 1}
        self._broker = broker
    
    def live_load(self, start_date=None, end_date=None):
        if not self._broker: raise ValueError("Broker is null")

        if not start_date:
            for obj in self._transactions.find(self._valid_tx_cond).sort([("date", pymongo.DESCENDING)]).limit(1):
                start_date = obj['date'] + datetime.timedelta(1)
        logger.debug("BEGIN: live load account %s from date: %s", self._account, start_date)
        json_obj = self._broker.get_transactions(self._account, start_date, end_date)
        transactions = self._get_transactions(json_obj)
        self._save(transactions, False)
        logger.debug("END: live load account %s from date: %s", self._account, start_date)
        return transactions

    def load(self, path, reload=True):
        transactions = self._parse_file(path)
        self._save(transactions, reload)
        return transactions

    def _parse_file(self, path):
        path = path.upper()
        if path.endswith(".CSV"): # schwab format
            return self._parse_csv(path)
        if path.endswith(".JSON"): # tdameritrade format
            return self._parse_json(path)
        raise ValueError(f"unsupported file extension: {path}")

    def _parse_csv(self, path):
        transactions = []
        with open(path) as csv_file:
            reader = csv.reader(csv_file)
            row = next(reader)[0]
            account = re.match('.*account ([^ ]+) .*', row).groups()[0][-4:]
            if account != self._account: return [], []

            for row in reader:
                try:
                    date, action, symbol, description, quantity, price, fee, amount, _ = row
                    tx = Transaction.from_dict(
                        account=account, date=date, action=action, symbol=symbol,
                        quantity=quantity, price=price, fee=fee, amount=amount, description=description)
                    transactions.append(tx)
                except Exception as e:
                    logger.error("Error occurred", exc_info=True)
                    continue
        return transactions

    def _parse_json(self, path):
        with open(path) as json_file:
            return self._get_transactions(json.load(json_file))

    def _get_transactions(self, json_obj):
        transactions = []
        for obj in json_obj:
            tx_item = obj['transactionItem']
            account = tx_item.get('accountId', None)
            if not account:
                logger.warning("ignore empty account: %s", obj)
                continue
            if str(account)[-4:] != self._account:
                continue
 
            description = obj['description']
            ignored = (description.upper() == "CASH ALTERNATIVES PURCHASE")
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

            tx_type = obj.get('type', None)
            subtype = obj.get('transactionSubType', None)
            action = ""
            if tx_type == "DIVIDEND_OR_INTEREST":
                if subtype == 'CA':
                    action = "INTEREST"
                elif subtype == 'OD': # ORDINARY DIVIDEND
                    action = "DIVIDEND"
                else:
                    ignored = True
            elif tx_type == "RECEIVE_AND_DELIVER":
                if subtype == 'OA':
                    action = "ASSIGNED"
                elif subtype == 'OX':
                    action = "EXPIRED"
                elif subtype == 'MI':
                    action = "INTEREST"
                elif subtype in ('PM', 'RM'): # ignore Money Market Purchase
                    ignored = True
                elif subtype in ('TI', 'TO'): # ignore transfer in/out
                    ignored = True
                else:
                    ignored = True
            elif tx_type == "TRADE":
                if subtype in ('RM', 'TI', '', None): # ignore unsettled transactions
                    ignored = True
                if subtype == 'OA' or subtype == 'OE': # assignment or exercise
                    action = "BTO"
                elif subtype == 'BY' or instruction == 'BUY':
                    if position_effect == 'OPENING' or position_effect is None:
                        action = "BTO"
                    elif position_effect == 'CLOSING':
                        action = "BTC"
                    elif position_effect == 'AUTOMATIC':
                        action = "BTC" # ?
                    else:
                        raise ValueError(f"unexpected position_effect: {position_effect}")
                elif subtype == 'SL' or instruction == 'SELL':
                    if position_effect == 'OPENING':
                        action = "STO"
                    elif position_effect == 'CLOSING':
                        action = "STC"
                    elif position_effect == 'AUTOMATIC' or position_effect is None:
                        action = "STC" # ?
                    else:
                        raise ValueError(f"unexpected position_effect: {position_effect}")
                else:
                    ignored = True
            elif tx_type == "JOURNAL":
                if subtype == 'IT': # internal transfer
                    action = "TRANSFER"
                else:
                    ignored = True
            else:
                ignored = True

            if action == "INTEREST":
                symbol = "" # ignore symbol MMDA1
            else:
                symbol = self._get_symbol(instrument)
                if not symbol and tx_type != "JOURNAL":
                    ignored = True

            tx = Transaction.from_dict(account=self._account, date=date, action=action,
                                       symbol=symbol, quantity=quantity, price=price,
                                       fee=total_fee, amount=amount, description=description,
                                       ignored=ignored)
            transactions.append(tx)
        return transactions

    def _save(self, transactions, reload):
        if reload:
            logger.info("BEGIN: reload")
            res = self._transactions.delete_many(self._account_cond)
            logger.debug("deleted %s transactions", res.deleted_count)
            res = self._transaction_groups.delete_many(self._account_cond)
            logger.debug("deleted %s transaction groups", res.deleted_count)
            logger.info("END: reload")
        logger.info("BEGIN: insert %s transations", len(transactions))
        for tx in transactions:
            self._transactions.insert_one(tx.to_json())
        logger.info("END: insert %s transations", len(transactions))

    @classmethod
    def _get_symbol(cls, instrument):
        symbol = instrument.get('symbol', None)
        if symbol: return symbol

        exp_date = instrument.get('optionExpirationDate', None)
        if not exp_date: return ""

        exp_date = datetime.datetime.strptime(exp_date[:10], "%Y-%m-%d")
        cusip = instrument['cusip']
        # format 0SOXL.NI20041000
        parts = cusip.split(".")
        ui = parts[0][1:]
        strike = int(parts[-1][4:]) / 1000
        symbol = f"{ui} {exp_date.strftime('%m/%d/%Y')} {strike:.2f} A"
        return symbol
