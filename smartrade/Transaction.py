# -*- coding: utf-8 -*-

from dateutil.parser import parse
from enum import Enum, IntEnum

import copy

class Action(IntEnum):
    BTO = -1
    STC = 1
    STO = 2
    BTC = -2
    # EXPIRED = 0
    ASSIGNED = 3
    TRANSFER = 4
    INTEREST = 5
    DIVIDEND = 6
    JOURNAL = 7
    INVALID = 8
 
    def is_open(self):
        return self in (Action.BTO, Action.STO)
 
    def is_close(self):
        return self in (Action.STC, Action.BTC, Action.ASSIGNED)

    @classmethod
    def from_str(cls, name, qty = 0):
        name = name.upper()
        if name in ('BTO', 'BUY', 'BUY TO OPEN'):
            return cls.BTO
        if name in ('STC', 'SELL', 'SELL TO CLOSE'):
            return cls.STC
        if name in ('STO', 'SELL TO OPEN'):
            return cls.STO
        if name in ('BTC', 'BUY TO CLOSE'):
            return cls.BTC
        if name in ('EXPIRED'):
            return cls.BTC if qty > 0 else cls.STC
        if name in ('ASSIGNED'):
            return cls.ASSIGNED
        if name in ('TRANSFER', 'MONEYLINK TRANSFER'):
            return cls.TRANSFER
        if name in ('DIVIDEND', 'CASH DIVIDEND', 'PR YR CASH DIV'):
            return cls.DIVIDEND
        if name in ('INTEREST', 'BANK INTEREST'):
            return cls.INTEREST
        if name in ('JOURNAL', 'JOURNALED SHARES'):
            return cls.JOURNAL

        return cls.INVALID


class InstrumentType(Enum):
    STOCK = 0
    CALL = 1
    PUT = -1
    OTHER = 2


class Symbol:
    def __init__(self, text):
        self._ui = None
        self._type = InstrumentType.OTHER
        self._strike = None
        if text == "": return

        tokens = text.split()
        self._ui = tokens[0]
        count = len(tokens)
        if count == 1:
            self._type = InstrumentType.STOCK
        elif count == 4:
            self._type = InstrumentType.CALL if tokens[3] == 'C' else InstrumentType.PUT
            self._strike = float(tokens[2])
            self._expired = parse(tokens[1])

    def is_option(self):
        return self._type == InstrumentType.CALL or self._type == InstrumentType.PUT

    def __eq__(self, other):
        if not isinstance(other, Symbol): return False

        return (self.ui == other.ui and self.type == other.type
                and self.strike == other.strike and self.expired == other.expired)

    def __repr__(self):
        s = str(self._type)
        if self._type != InstrumentType.OTHER:
            s += ": " + self._ui
            if self._type == InstrumentType.CALL or self._type == InstrumentType.PUT:
                s += " strike: {}, expired: {}".format(self._strike, self._expired)
        return s

    def __str__(self):
        return self.__repr__()

    @property
    def type(self):
        return self._type

    @property
    def ui(self):
        return self._ui

    @property
    def strike(self):
        return self._strike

    @property
    def expired(self):
        return self._expired


class Transaction:

    @classmethod
    def from_doc(cls, doc):
        self = cls()
        self._valid = True
        for attr in ['date', 'quantity', 'price', 'fee', 'amount', 'ui', 'strike', 'expired', 'description', 'grouped']:
            setattr(self, "_" + attr, doc.get(attr, None))
        assert(self.quantity >= 0)
        self._action = Action.from_str(doc['action'])
        symbol = ""
        ui = doc.get('ui', None)
        if ui:
            symbol += ui
            expired = doc.get('expired', None)
            if expired:
                symbol += " " + expired.strftime('%m/%d/%Y')
                symbol += " " + str(doc['strike'])
                symbol += " " + ('C' if doc['type'] == 'CALL' else 'P')
        self._symbol = Symbol(symbol)
        return self

    @classmethod
    def from_dict(cls, **map):
        self = cls()
        self._valid = False
        qty = self._get_int(map['quantity'])
        self._action = Action.from_str(map['action'].strip(), qty)
        self._quantity = abs(qty)
        self._description = map.get('description', '')
        self._grouped = False
        if self._action is Action.INVALID:
            return self

        try:
            self._date = parse(map['date'].strip().split()[0])
        except Exception:
            return self

        self._symbol = Symbol(map['symbol'].strip())
        self._price = self._get_money(map['price'])
        self._fee = self._get_money(map['fee'])
        self._amount = self._get_money(map['amount'])
        self._valid = self._verify()
        return self

    def _verify(self):
        action = self.action
        if action >= Action.ASSIGNED: return True

        amt = self.share * self._price * (1 if self._action > 0 else -1) - self._fee 
        if abs(amt - self._amount) > 1e-6:
            # print("?", amt, "!=", self._amount)
            return False
        return True

    def merge(self, other):
        if self.symbol != other.symbol or self.action != other.action or self.date != other.date:
            return

        res = copy.copy(self)
        res._fee += other.fee
        res._amount += other.amount
        res._quantity += other.quantity
        res._price = (res.amount - res.fee) / res.share
        return res

    def remove(self, qty):
        if qty <= 0 or qty > self.quantity:
            raise ValueError("qty {} should be between 1 and {}".format(qty, self.quantity))

        other = copy.copy(self)
        ratio = qty / self.quantity
        other._fee *= ratio
        self._fee -= other._fee
        other._amount *= ratio
        self._amount -= other._amount
        other._quantity = qty
        self._quantity -= qty
        return other
 
    def same_option_group(self, other):
        if self.date != other.date: return False

        symbol1 = self.symbol
        symbol2 = other.symbol
        return (symbol1.is_option() and symbol2.is_option()
                and symbol1.ui == symbol2.ui)

    def is_option(self):
        return self._symbol.is_option()

    def _get_int(self, text):
        try:
            return int(text.strip())
        except Exception:
            return 0

    def _get_money(self, text):
        text = text.strip()
        if len(text) == 0 or (text[0] != '$' and text[0] != '-'): return 0
        return -float(text[2:]) if text[0] == '-' else float(text[1:])

    def is_valid(self):
        return self._valid
 
    def to_json(self, full=True):
        symbol = self.symbol
        json = {
            'date': self.date,
            'action': str(self.action).split('.')[1],
            'quantity': self.quantity,
            'price': self.price,
            'fee': self.fee,
            'amount': self.amount,
            'type': str(symbol.type).split('.')[1],
        }
        if full:
            json['description'] = self.description
            json['grouped'] = self.grouped
        if symbol.ui:
            json['ui'] = symbol.ui
            if symbol.strike:
                json['strike'] = symbol.strike
                json['expired'] = symbol.expired
        return json

    def __repr__(self):
        if self.is_valid():
            return "date: {}, action: {}, symbol: ({}), price: {}, quantity: {}, fee: {}, amount: {}".format(
                self.date, str(self.action), self.symbol,
                "{:.5f}".format(self.price), self.quantity,
                "{:.2f}".format(self.fee), self.amount)
        return "INVALID transaction"

    def __str__(self):
        return self.__repr__()

    @property
    def date(self):
        return self._date

    @property
    def action(self):
        return self._action

    @property
    def symbol(self):
        return self._symbol

    @property
    def price(self):
        return self._price

    @property
    def quantity(self):
        return self._quantity

    @property
    def share(self):
        return self._quantity * (100 if self.is_option() else 1)
    
    @property
    def fee(self):
        return self._fee

    @property
    def amount(self):
        return self._amount

    @property
    def description(self):
        return self._description

    @property
    def grouped(self):
        return self._grouped
