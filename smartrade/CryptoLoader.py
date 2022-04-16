# -*- coding: utf-8 -*-

import csv
import re

from smartrade import app_logger
from smartrade.CryptoTransaction import CryptoTransaction, CryptoAction

logger = app_logger.get_logger(__name__)

class CryptoLoader:
    ERROR = 1e-8

    def __init__(self, broker=None):
        self._broker = broker

    def load(self, path, broker, init_pos={}):
        if broker == 'coinbase':
            return self._parse_coinbase(path, init_pos)
        if broker == 'gemini':
            return self._parse_gemini(path, init_pos)

    def _parse_coinbase(self, path, init_pos):
        transactions = []
        symbols = set()
        with open(path) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            prev = None
            total_amount = 0
            for symbol, val in init_pos.items():
                if symbol == 'USD':
                    total_amount = val
                else:
                    amount = val['amount']
                    qty = val['quantity']
                    action = CryptoAction.BUY if amount < 0 else CryptoAction.SELL
                    price = abs(amount / qty)
                    tx = CryptoTransaction.from_dict(
                        date=val['date'], symbol=symbol, quantity=qty, amount=amount, action=action, fee=0, price=price)
                    transactions.append(tx)

            while True:
                cur = prev or next(reader, None)
                prev = None
                if not cur:
                    break

                try:
                    portfolio, type_, time, amount, balance, unit, transfer_id, trade_id, order_id = cur
                    if portfolio.startswith('#'): continue

                    amount = float(amount)
                    symbols.add(unit)
                    if unit == 'USD':
                        total_amount += amount
                        assert (abs(total_amount - float(balance)) < self.ERROR), f"{total_amount} should = {balance}"
                    if type_ == 'deposit' or type_ == 'withdrawal':
                        amt = amount if unit == 'USD' else 0
                        tx = CryptoTransaction.from_dict(
                            date=time, symbol=unit, quantity=amount, amount=amt, action=CryptoAction.TRANSFER, fee=0, price=0)
                        transactions.append(tx)
                        continue

                    assert type_ == 'match'
                    quantity = 0
                    symbol = None
                    if unit != 'USD':
                        symbol = unit
                        quantity = amount
                        amount = 0
                    fee = 0
                    while True:
                        next_row = next(reader, None)
                        if not next_row:
                            break

                        portfolio2, type2, time2, amount2, balance2, unit2, transfer_id2, trade_id2, order_id2 = next_row
                        amount2 = float(amount2)
                        if order_id != order_id2:
                            prev = next_row
                            break

                        if unit2 == 'USD':
                            total_amount += amount2
                            assert (abs(total_amount - float(balance2)) < self.ERROR), f"{total_amount} should = {balance2}"

                        if type2 == 'fee':
                            fee += amount2
                            continue

                        assert type2 == 'match'
                        if unit2 == 'USD':
                            amount += amount2
                        else:
                            if not symbol:
                                symbol = unit2
                                symbols.add(symbol)
                            assert unit2 == symbol, f"{unit2} should be the same as {symbol}"
                            quantity += amount2
                    price = abs(amount / quantity)
                    amount += fee
                    action = CryptoAction.BUY if amount < 0 else CryptoAction.SELL
                    tx = CryptoTransaction.from_dict(
                        date=time, symbol=symbol, quantity=quantity, amount=amount, fee=fee, price=price, action=action)
                    transactions.append(tx)

                except Exception as e:
                    logger.error("Error occurred", exc_info=True)
                    break
                    # continue

        return transactions, symbols

    @classmethod
    def _get_amount(cls, amount):
        sign = 1
        if '$' in amount:
            neg_pat = re.match('\(\$(.+)\)', amount)
            if neg_pat:
                sign = -1
                amount = neg_pat.groups()[0]
            else:
                amount = amount[1:]  # remove '$'
        else:  # (10 ETH)
            neg_pat = re.match('\(([^ ]+) .+\)', amount)
            if neg_pat:
                sign = -1
                amount = neg_pat.groups()[0]
            else:
                amount = amount.split()[0] if amount else "0"
        return float(amount.replace(',', '')) * sign

    def _parse_gemini(self, path, init_pos):
        transactions = []
        symbols = set()
        with open(path) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            prev = None
            total_amount = 0
            for symbol, val in init_pos.items():
                if symbol == 'USD':
                    total_amount = val
                else:
                    amount = val['amount']
                    qty = val['quantity']
                    action = CryptoAction.BUY if amount < 0 else CryptoAction.SELL
                    price = abs(amount / qty)
                    tx = CryptoTransaction.from_dict(
                        date=val['date'], symbol=symbol, quantity=qty, amount=amount, action=action, fee=0, price=price)
                    transactions.append(tx)

            while True:
                cur = prev or next(reader, None)
                prev = None
                if not cur:
                    break

                try:
                    date, time, type_, symbol, desc, _, _, amount, fee, balance, * \
                        coin_amt, trade_id, order_id, order_date, order_time, _, _, _, _, _, _, _ = cur
                    if not date or date.startswith('#'): continue

                    crypto = re.match('(.+?)(USD)?$', symbol)
                    symbol = crypto.groups()[0]
                    assert(symbol)
                    quantity = 0
                    amount = self._get_amount(amount)
                    for amt in coin_amt:
                        if symbol in amt:
                            quantity = self._get_amount(amt)
                            break
                    if type_ == 'Credit' or type_ == 'Debit':
                        tx = CryptoTransaction.from_dict(
                            date=date, symbol=symbol, quantity=quantity, amount=amount, action=CryptoAction.TRANSFER, fee=0, price=0)
                        transactions.append(tx)
                        continue

                    symbols.add(symbol)

                    fee = self._get_amount(fee)
                    balance = self._get_amount(balance)
                    #TODO: assert balance(inc. coin balance)
                    while True:
                        next_row = next(reader, None)
                        if not next_row:
                            break

                        date2, time2, type_2, symbol2, desc2, _, _, amount2, fee2, balance2, * \
                            coin_amt2, trade_id2, order_id2, _, _, _, _, _, _, _, _, _ = next_row
                        if not order_id or order_id != order_id2:
                            prev = next_row
                            break

                        for amt in coin_amt2:
                            if symbol in amt:
                                quantity += self._get_amount(amt)
                                break

                        amount += self._get_amount(amount2)
                        fee += self._get_amount(fee2)
                    price = abs(amount / quantity)
                    amount += fee
                    action = CryptoAction.BUY if amount < 0 else CryptoAction.SELL
                    tx = CryptoTransaction.from_dict(
                        date=date, symbol=symbol, quantity=quantity, amount=amount, fee=fee, price=price, action=action)
                    transactions.append(tx)

                except Exception as e:
                    logger.error("Error occurred", exc_info=True)
                    break

        return transactions, symbols
