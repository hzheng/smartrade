# -*- coding: utf-8 -*-

import copy
import re
from datetime import datetime
from enum import Enum, IntEnum

from bson import ObjectId
from dateutil.parser import parse, ParserError

from smartrade import app_logger
from smartrade.utils import check

logger = app_logger.get_logger(__name__)

class Validity(IntEnum):
    INVALID = -1
    IGNORED = 0
    VALID = 1

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
 
    def __format__(self, _):
        return str(self).split(".")[1]

    @classmethod
    def from_str(cls, name):
        if name.startswith("Action."):
            name = name[7:]
        name = name.upper()

        if name in ('BTO', 'BUY', 'BUY TO OPEN', 'BUY_TO_OPEN', 'REINVEST SHARES'):
            return cls.BTO
        if name in ('STC', 'SELL', 'SELL TO CLOSE', 'SELL_TO_CLOSE'):
            return cls.STC
        if name in ('STO', 'SELL TO OPEN', 'SELL_TO_OPEN'):
            return cls.STO
        if name in ('BTC', 'BUY TO CLOSE', 'BUY_TO_CLOSE'):
            return cls.BTC
        if name in ('EXPIRED', ):
            # return cls.BTC if qty > 0 else cls.STC
            return cls.EXPIRED
        if name in ('ASSIGNED', ):
            return cls.ASSIGNED
        if name in ('EXERCISE', 'EXCHANGE OR EXERCISE'):
            return cls.EXERCISE
        if name in ('DIVIDEND', 'CASH DIVIDEND', 'PR YR CASH DIV', 'PR YR DIV REINVEST', 'REINVEST DIVIDEND', 'QUALIFIED DIVIDEND'):
            return cls.DIVIDEND
        if name in ('INTEREST', 'BANK INTEREST', 'PROMOTIONAL AWARD'):
            return cls.INTEREST
        if name in ('TRANSFER', 'MONEYLINK TRANSFER', 'FUNDS RECEIVED', 'FUNDS PAID', 'SECURITY TRANSFER'):
            return cls.TRANSFER
        if name in ('JOURNAL', 'JOURNALED SHARES'):
            return cls.JOURNAL

        logger.warning("invalid Action name: %s", name)
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

    def __format__(self, _):
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
        elif " " in text or not text[-1].isdigit():
            self._parse2(text)
        else:
            self._parse3(text)

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

    def _parse3(self, text):
        """Format: AMD230120C00120000"""
        res = re.match('(\D+)(\d{6})(.)(\d+)', text)
        self._ui, date_str, opt_type, strike = res.groups()
        self._type = InstrumentType.from_str(opt_type)
        self._strike = int(strike) / 1000
        self._expired = datetime.strptime(date_str, '%y%m%d')

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
        
        return f"{self.ui} {self.expired.strftime('%m/%d/%Y')} {self.strike:.2f} {self.type}"

    def __format__(self, spec):
        if not self.expired: return self.ui

        if not spec:
            return f"{self.ui}_{self.expired.strftime('%m%d%y')}{self.type}{self.strike:g}"

        strike = f"{self.strike * 1000}".rstrip('0').rstrip('.').zfill(8)
        return f"{self.ui}{self.expired.strftime('%y%m%d')}{self.type}{strike}"

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

    def __init__(self) -> None:
        self._id = None
        self._date = None
        self._symbol = ""
        self._price = 0
        self._fee = 0
        self._amount = 0
        self._valid = Validity.INVALID
        self._merge_parent = None
        self._slice_parent = None
        self._grouped = None

    @classmethod
    def from_doc(cls, doc):
        self = cls()
        self._valid = doc.get('valid', True)
        self._id = doc.get('_id', None)
        for attr in ['account', 'date', 'quantity', 'price', 'fee', 'amount', 'ui', 'strike', 'expired', 'description', 'merge_parent', 'slice_parent', 'grouped']:
            setattr(self, "_" + attr, doc.get(attr, None))
        check(self.quantity is None or self.quantity >= 0, f"quantity {self.quantity} can't be negative")
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
        self._account = map['account']
        qty = self._get_quantity(map['quantity'])
        self._action = Action.from_str(map['action'].strip())
        self._quantity = None if qty is None else abs(qty) 
        self._description = map.get('description', '')
        if map.get('ignored', False) or self.description.startswith("#"):
            self._valid = Validity.IGNORED

        self._amount = self._get_money(map['amount'])
        self._price = self._get_money(map['price'])
        self._fee = self._get_money(map['fee'])
        try:
            date = map['date'].strip().split()[0]
            self._date = parse(date)
        except ParserError:
            logger.warning("wrong date format: %s", date)
            return self
        except Exception:
            logger.error("Error occurred", exc_info=True)
            return self

        if self.valid == Validity.IGNORED or self.action == Action.INVALID:
            return self

        self._symbol = Symbol(map['symbol'].strip())
        self._valid = self._verify()
        return self

    def cash_sign(self):
        return -1 if abs(self.action) == Action.BTC else 1
 
    def position_sign(self, balance):
        if self.action in(Action.BTO, Action.BTC, Action.ASSIGNED): return 1

        if self.action == Action.EXPIRED:
            return -1 if balance > 0 else 1

        return -1

    def _verify(self):
        action = self.action
        if action >= Action.EXERCISE: return Validity.VALID

        amt = self.share * self.price * self.cash_sign() - self.fee 
        if abs(amt - self.amount) > self.price * 0.001: # assume minimal amount is 0.001
            logger.warning(f"amount {amt} and {self.amount} don't match in %s", self)
            return Validity.INVALID
        return Validity.VALID

    def merge(self, other):
        if self.account != other.account or self.symbol != other.symbol or self.action != other.action or self.date != other.date:
            return None, None

        merged = (self.merge_parent == self.id)
        if merged: # already created merge parent
            res = self
        else:
            res = copy.copy(self)
            res._merge_parent = res._id = ObjectId()
        res._fee += other.fee
        res._amount += other.amount
        res._quantity += other.quantity
        res._price = abs((res.amount - res.fee) / res.share)
        self._merge_parent = other._merge_parent = res.id
        return res, not merged

    def slice(self, qty):
        if qty <= 0 or qty > self.quantity:
            raise ValueError(f"qty {qty} should be between 0 and {self.quantity}")

        original = copy.copy(self)
        if self.quantity - qty <= 1e-6:
            self._quantity = 0
            return original, original, False

        sliced = copy.copy(self)
        # set slice parents
        is_sliced = self.is_sliced() # has self been sliced already?
        slice_parent = self.slice_parent if is_sliced else self.id
        original._slice_parent = self._slice_parent = sliced._slice_parent = slice_parent
        # create ID's for virtual transactions
        self._id = ObjectId()
        sliced._id = ObjectId()
        # slice numbers
        ratio = qty / self.quantity
        sliced._fee *= ratio
        self._fee -= sliced._fee
        sliced._amount *= ratio
        self._amount -= sliced._amount
        sliced._quantity = qty
        self._quantity -= qty
        # don't create intermediate sliced transaction
        #return sliced, None if is_sliced else original
        return sliced, original, not is_sliced

    def is_sliced(self):
        """Is the transaction sliced?"""
        return self.slice_parent and self.slice_parent != self.id

    def is_merged(self):
        """Is the transaction merged?"""
        return self.merge_parent and self.merge_parent != self.id and self.merge_parent != self.slice_parent

    def is_virtual(self):
        """Is the transaction virtual?(either a merged parent or a split child)"""
        return self.merge_parent == self.id or self.is_sliced()

    def is_original(self):
        """Is the transaction original?"""
        return not self.is_virtual()

    def is_effective(self):
        """Is the transaction effective to be used in group?"""
        return (not self.is_merged()) and (self.slice_parent != self.id)
 
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
 
    def to_json(self, hide=None, serialize=False):
        def stringify(value):
            if not serialize: return value
            return str(value) if value else None

        symbol = self.symbol
        json = {
            'date': self.date,
            'quantity': self.quantity,
            'price': self.price,
            'fee': self.fee,
            'amount': self.amount,
            'action': format(self.action)
        }
        if not hide and self.valid == Validity.VALID:
            json['type'] = str(symbol.type).split('.')[1]
        if hide is None:
            if self.id:
                json['_id'] = stringify(self.id)
            json['account'] = self.account
            json['description'] = self.description
            json['grouped'] = self.grouped
            json['merge_parent'] = stringify(self.merge_parent)
            json['slice_parent'] = stringify(self.slice_parent)
            json['valid'] = self.valid
        if self.valid == Validity.VALID and symbol.ui:
            if hide is None:
                json['ui'] = symbol.ui
            if symbol.strike and not hide:
                json['strike'] = symbol.strike
                json['expired'] = symbol.expired
        if serialize:
            json['symbol'] = str(symbol)
        return json

    def __repr__(self):
        return (f"account={self.account}, date={self.date}, action={str(self.action)}, symbol={self.symbol},"
                f" price={self.price:.4f}, quantity={self.quantity},"
                f" fee={self.fee:.2f}, amount={self.amount}, desc={self.description}, valid={self.valid}"
                f" id={self.id}, merge_parent={self.merge_parent}, slice_parent={self.slice_parent}")

    def __str__(self):
        return self.__repr__()

    @property
    def id(self):
        return self._id

    @property
    def merge_parent(self):
        return self._merge_parent

    @property
    def slice_parent(self):
        return self._slice_parent

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
    def valid(self):
        return self._valid

    @property
    def grouped(self):
        return self._grouped
    
    @grouped.setter
    def grouped(self, value):
        self._grouped = value
