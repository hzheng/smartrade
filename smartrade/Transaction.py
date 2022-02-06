# -*- coding: utf-8 -*-

from dateutil.parser import parse
from enum import Enum, IntEnum

class Action(IntEnum):
    BTO = -1
    STC = 1
    STO = 2
    BTC = -2
    EXPIRED = 0
    ASSIGNED = 3
    TRANSFER = 4
    INTEREST = 5
    DIVIDEND = 6
    JOURNAL = 7
    INVALID = 8
 
    @classmethod
    def from_str(cls, name):
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
            return cls.EXPIRED
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
        self._type = InstrumentType.OTHER
        self._strike = None
        self._ui = None
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
        for attr in ['date', 'quantity', 'price', 'fee', 'amount', 'ui', 'strike', 'expired', 'description']:
            setattr(self, "_" + attr, doc.get(attr, None))
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
        self._action = Action.from_str(map['action'].strip())
        self._description = map['description']
        if self._action is Action.INVALID:
            return self

        try:
            date = parse(map['date'].strip().split()[0])
        except Exception:
            return self

        self._date = date
        self._symbol = Symbol(map['symbol'].strip())
        self._price = self._get_money(map['price'])
        self._fee = self._get_money(map['fee'])
        self._amount = self._get_money(map['amount'])
        self._quantity = self._get_int(map['quantity'])
        self._valid = self._verify()
        return self

    def _verify(self):
        action = self.action
        if action >= Action.ASSIGNED: return True

        quantity = self._quantity
        if self.is_option():
            quantity *= 100
        amt = quantity * self._price * (1 if self._action > 0 else -1) - self._fee 
        if abs(amt - self._amount) > 1e-6:
            # print("?", amt, "!=", self._amount)
            return False
        return True

    def is_option(self):
        return self._symbol.is_option()

    def _get_int(self, text):
        text = text.strip()
        return 0 if len(text) == 0 else int(text)

    def _get_money(self, text):
        text = text.strip()
        if len(text) == 0 or (text[0] != '$' and text[0] != '-'): return 0
        return -float(text[2:]) if text[0] == '-' else float(text[1:])

    def is_valid(self):
        return self._valid

    def __repr__(self):
        if self.is_valid():
            return "date: {}, action: {}, symbol: ({}), price: {}, quantity: {}, fee: {}, amount: {}".format(
                self.date, str(self.action), self.symbol, self.price, self.quantity, self.fee, self.amount)
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
    def fee(self):
        return self._fee

    @property
    def amount(self):
        return self._amount

    @property
    def description(self):
        return self._description
