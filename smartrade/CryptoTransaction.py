# -*- coding: utf-8 -*-

import copy
import heapq

from collections import deque
from enum import IntEnum

from smartrade import app_logger

logger = app_logger.get_logger(__name__)


class CryptoAction(IntEnum):
    BUY = -1
    SELL = 1
    TRANSFER = 0


class CryptoTransaction:
    ERROR = 1e-8

    def __init__(self) -> None:
        self._id = None
        self._date = None
        self._quantity = None
        self._symbol = ""
        self._price = 0
        self._fee = 0
        self._amount = 0
        self._action = 0

    @classmethod
    def from_dict(cls, **map):
        self = cls()
        self._date = map['date']
        self._quantity = map['quantity']
        self._symbol = map['symbol']
        self._action = map['action']
        self._price = map['price']
        self._fee = map['fee']
        self._amount = map['amount']
        return self

    def slice(self, qty):
        # if qty <= 0 or qty > self.quantity:
        #    raise ValueError(f"qty {qty} should be between 0 and {self.quantity}")

        if self.quantity - qty <= self.ERROR:
            self._quantity = 0
            self._amount = 0
            return False

        ratio = 1 - qty / self.quantity
        self._fee *= ratio
        self._amount *= ratio
        self._quantity -= qty
        return True

    @property
    def date(self):
        return self._date

    @property
    def symbol(self):
        return self._symbol

    @property
    def action(self):
        return self._action

    @property
    def price(self):
        return self._price

    @property
    def quantity(self):
        return self._quantity

    @property
    def fee(self):
        return self._fee

    @property
    def amount(self):
        return self._amount

    def __lt__(self, other):
        return self.price > other.price

    def __repr__(self):
        return (f"date={self.date}, symbol={self.symbol}, action={self.action},"
                f" price={self.price:.4f}, quantity={self.quantity},"
                f" fee={self.fee:.2f}, amount={self.amount}")

    def __str__(self):
        return self.__repr__()

    @classmethod
    def get_pnl_from_last(cls, transactions, include_transfer=False):
        """find last buy transactions with the amount of current position. essentially fifo"""
        tx_list = [tx for tx in transactions if (
            include_transfer or tx.action != CryptoAction.TRANSFER)]
        position = 0
        amount = 0
        cost = 0
        proceeds = 0
        for tx in tx_list:
            amount += tx.amount
            position += tx.quantity
            if tx.action == CryptoAction.BUY:
                cost += tx.amount
            else:
                proceeds += tx.amount
        if position == 0:
            return amount, cost, proceeds, 0, 0

        pos = 0
        buy = 0
        for tx in tx_list[::-1]:
            if tx.quantity <= 0:
                continue

            need = position - pos
            if tx.quantity <= need - cls.ERROR:
                pos += tx.quantity
                buy += tx.amount
                continue

            buy += tx.amount * (need / tx.quantity)
            break
        return amount - buy, cost - buy, proceeds, buy, position

    @classmethod
    def get_pnl(cls, transactions, fifo, include_transfer=False):
        """algo: 1: fifo, -1: lifo, 0: hifo"""
        tx_list = [copy.copy(tx) for tx in transactions if (
            include_transfer or tx.action != CryptoAction.TRANSFER)]
        buy_queue = deque() if fifo != 0 else []
        pnl = 0
        cost = 0
        proceeds = 0
        for tx in tx_list:
            if tx.quantity > 0:
                # if tx.action == CryptoAction.BUY
                cost += tx.amount
                if fifo != 0:
                    buy_queue.append(tx)
                else:
                    heapq.heappush(buy_queue, tx)
                continue

            assert tx.action == CryptoAction.SELL
            sell_qty = -tx.quantity
            proceeds += tx.amount
            pnl += tx.amount
            done = False
            while not done:
                first_buy = buy_queue[0 if fifo >= 0 else -1]
                buy_amount = first_buy.amount
                buy_qty = first_buy.quantity
                if first_buy.slice(sell_qty):
                    done = True
                else:
                    if fifo > 0:
                        buy_queue.popleft()
                    elif fifo < 0:
                        buy_queue.pop()
                    else:
                        heapq.heappop(buy_queue)
                    sell_qty -= buy_qty
                    done = abs(sell_qty) < cls.ERROR
                pnl += buy_amount - first_buy.amount
        latest_cost = sum(tx.amount for tx in buy_queue)
        pos = sum(tx.quantity for tx in buy_queue)
        return pnl, cost - latest_cost, proceeds, latest_cost, pos
