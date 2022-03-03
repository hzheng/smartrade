# -*- coding: utf-8 -*-

import copy
from enum import Enum, IntEnum

from dateutil.parser import parse

class Action(IntEnum):
    BTO = -2
    STO = -1
    STC = 1
    BTC = 2
    EXPIRED = 3
    ASSIGNED = 4
    EXERCISE = 5
    TRANSFER = 6
    INTEREST = 7
    DIVIDEND = 8
    JOURNAL = 9
    INVALID = 10
 
    def is_open(self):
        return self <= Action.STO
 
    def is_close(self):
        return Action.STC <= self <= Action.EXERCISE
 
    def to_str(self):
        return str(self).split(".")[1]

    @classmethod
    def from_str(cls, name):
        if name.startswith("Action."):
            name = name[7:]
        name = name.upper()
        if name in ('BTO', 'BUY', 'BUY TO OPEN', 'REINVEST SHARES'):
            return cls.BTO
        if name in ('STC', 'SELL', 'SELL TO CLOSE'):
            return cls.STC
        if name in ('STO', 'SELL TO OPEN'):
            return cls.STO
        if name in ('BTC', 'BUY TO CLOSE'):
            return cls.BTC
        if name in ('EXPIRED'):
            # return cls.BTC if qty > 0 else cls.STC
            return cls.EXPIRED
        if name in ('ASSIGNED'):
            return cls.ASSIGNED
        if name in ('EXCHANGE OR EXERCISE'):
            return cls.EXERCISE
        if name in ('TRANSFER', 'MONEYLINK TRANSFER'):
            return cls.TRANSFER
        if name in ('DIVIDEND', 'CASH DIVIDEND', 'PR YR CASH DIV', 'PR YR DIV REINVEST', 'REINVEST DIVIDEND'):
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
    AUTO = 2
    OTHER = 2

    def match(self, other):
        return self == other or self == self.AUTO  or other == self.AUTO

    @classmethod
    def from_str(cls, text):
        if text == 'S': return cls.STOCK
        if text == 'C': return cls.CALL
        if text == 'P': return cls.PUT
        if text == 'A': return cls.AUTO
        raise ValueError(f"Unknown {cls.__name__}: {text}")

    def to_str(self):
        if self == self.STOCK: return 'S'
        if self == self.CALL: return 'C'
        if self == self.PUT: return 'P'
        if self == self.AUTO: return 'A'

class Symbol:
    def __init__(self, text):
        self._ui = None
        self._type = InstrumentType.OTHER
        self._strike = None
        self._expired = None
        if text == "": return

        if "_" in text:
            self._parse1(text)
        else:
            self._parse2(text)

    def _parse1(self, text):
        """Format: HOOD_031122C14.5"""
        self._ui, tokens = text.split('_')
        self._type = InstrumentType.from_str(tokens[6])
        self._strike = float(tokens[7:])
        self._expired = parse(tokens[:6])

    def _parse2(self, text):
        """Format: TWTR 02/04/2022 38.00 C"""
        tokens = text.split()
        self._ui = tokens[0]
        count = len(tokens)
        if count == 1:
            self._type = InstrumentType.STOCK
        elif count == 4:
            self._type = InstrumentType.from_str(tokens[3])
            self._strike = float(tokens[2])
            self._expired = parse(tokens[1])

    def is_option(self):
        return self.type == InstrumentType.CALL or self.type == InstrumentType.PUT

    def __eq__(self, other):
        if not isinstance(other, Symbol): return False

        return (self.ui == other.ui and self.type.match(other.type)
                and self.strike == other.strike and self.expired == other.expired)

    def __repr__(self):
        s = str(self.type)
        if self._type != InstrumentType.OTHER:
            s += ": " + self.ui
            if self.type == InstrumentType.CALL or self.type == InstrumentType.PUT:
                s += f" strike: {self.strike}, expired: {self.expired}"
        return s

    def __str__(self):
        if not self.expired: return self.ui or ""
        
        return f"{self.ui} {self.expired.strftime('%m/%d/%Y')} {self.strike:.2f} {self.type.to_str()}"

    def to_str(self):
        if not self.expired: return self.ui

        return f"{self.ui}_{self.expired.strftime('%m%d%y')}{self.type.to_str()}{self.strike:g}"

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
        for attr in ['account', 'date', 'quantity', 'price', 'fee', 'amount', 'ui', 'strike', 'expired', 'description', 'grouped']:
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
                symbol += " " + doc['type'][0]
        self._symbol = Symbol(symbol)
        return self

    @classmethod
    def from_dict(cls, **map):
        self = cls()
        self._valid = False
        self._account = map['account']
        qty = self._get_quantity(map['quantity'])
        self._action = Action.from_str(map['action'].strip())
        self._quantity = None if qty is None else abs(qty) 
        self._description = map.get('description', '')
        self._grouped = False
        self._date = None
        self._symbol = ""
        self._price = 0
        self._fee = 0
        self._amount = 0
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
        if action >= Action.EXERCISE: return True

        amt = self.share * self.price * (-1 if abs(self.action) == Action.BTC else 1) - self.fee 
        if abs(amt - self.amount) > 1e-2:
            # print("?", amt, "!=", self.amount, self)
            return False
        return True

    def merge(self, other):
        if self.account != other.account or self.symbol != other.symbol or self.action != other.action or self.date != other.date:
            return

        res = copy.copy(self)
        res._fee += other.fee
        res._amount += other.amount
        res._quantity += other.quantity
        res._price = abs((res.amount - res.fee) / res.share)
        return res

    def remove(self, qty):
        if qty <= 0 or qty > self.quantity:
            raise ValueError(f"qty {qty} should be between 0 and {self.quantity}")

        other = copy.copy(self)
        ratio = qty / self.quantity
        other._fee *= ratio
        self._fee -= other._fee
        other._amount *= ratio
        self._amount -= other._amount
        other._quantity = qty
        self._quantity -= qty
        return other
 
    def same_group(self, other):
        return self.account == other.account and self.date == other.date and self.symbol.ui == other.symbol.ui

    def is_option(self):
        return self._symbol.is_option()

    def closed_by(self, other):
        if not (self.action.is_open() and other.action.is_close()): return False
        if self.date > other.date: return False

        return self.symbol == other.symbol

    def _get_quantity(self, text):
        if not isinstance(text, str): return text

        try:
            return float(text.strip())
        except Exception:
            return 0

    def _get_money(self, text):
        if not isinstance(text, str): return text

        text = text.strip()
        if len(text) == 0 or (text[0] != '$' and text[0] != '-'): return 0
        return -float(text[2:]) if text[0] == '-' else float(text[1:])

    def is_valid(self):
        return self._valid
 
    def to_json(self, hide=None):
        symbol = self.symbol
        json = {
            'date': self.date,
            'quantity': self.quantity,
            'price': self.price,
            'fee': self.fee,
            'amount': self.amount,
            'action': str(self.action).split('.')[1]
        }
        if not hide:
            json['type'] = str(symbol.type).split('.')[1]
        if hide is None:
            json['account'] = self.account
            json['description'] = self.description
            json['grouped'] = self.grouped
        if symbol.ui:
            if hide is None:
                json['ui'] = symbol.ui
            if symbol.strike and not hide:
                json['strike'] = symbol.strike
                json['expired'] = symbol.expired
        return json

    def __repr__(self):
        return (f"account={self.account}, date={self.date}, action={str(self.action)}, symbol={self.symbol},"
                f" price={self.price:.4f}, quantity={self.quantity},"
                f" fee={self.fee:.2f}, amount={self.amount}{'' if self.is_valid() else ' INVALID'}")

    def __str__(self):
        return self.__repr__()

    @property
    def account(self):
        return self._account

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
        return self.quantity * (100 if self.is_option() else 1)
    
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
