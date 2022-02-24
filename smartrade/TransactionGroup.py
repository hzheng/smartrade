# -*- coding: utf-8 -*-

from collections import deque
from datetime import datetime
import math

from smartrade.Transaction import InstrumentType, Transaction, Action

class TransactionGroup:

    _broker = None

    def __init__(self, leading_transactions=None):
        self._chains = {tx: [] for tx in leading_transactions} if leading_transactions else {}
        self._positions = None
        self._cost = None
        self._profit = None
        self._total = None
        self._ui = None
        self._duration = None
        self._roi = None

    @classmethod
    def set_broker(cls, broker):
        cls._broker = broker

    @classmethod
    def _merge_docs(cls, transaction_docs):
        tx = [Transaction.from_doc(doc) for doc in transaction_docs]
        return cls.merge(tx)

    @classmethod
    def merge(cls, transactions):
        if not transactions: return []

        res = [transactions[0]]
        for tx in transactions[1:]:
            prev = res[-1]
            cur = prev.merge(tx)
            if cur:
                res[-1] = cur
            else:
                res.append(tx)
        return res

    @classmethod
    def combine(cls, transactions):
        if not transactions: return []

        res = [[]]
        for tx in transactions:
            prev = res[-1]
            if not prev or tx.same_group(prev[0]):
                prev.append(tx)
            else:
                res.append([tx])
        return res
    
    @classmethod
    def assemble(cls, leading_tx, following_tx):
        merged_leading_tx = cls._merge_docs(leading_tx)
        groups = [cls(tx_list) for tx_list in cls.combine(merged_leading_tx)]
        merged_following_tx = cls._merge_docs(following_tx)
        following_tx_queue = deque(cls.combine(merged_following_tx))
        while following_tx_queue:
            tx_list = following_tx_queue.popleft()
            close_tx_list = [tx for tx in tx_list if tx.action.is_close() and tx.quantity > 0]
            if not close_tx_list: continue

            open_tx_list = [tx for tx in tx_list if tx.action.is_open()]
            grouped = False
            for group in groups: # search for matching transactions
                if group._followed_by(close_tx_list):
                    for tx in open_tx_list:
                        group._chains[tx] = []
                    following_tx_queue.appendleft(close_tx_list)
                    grouped = True
                    break
            assert(grouped)
        return groups
    
    def _followed_by(self, following_tx_list):
        res = False
        for open_tx, close_tx_list in self._chains.items():
            opened = open_tx.quantity
            for close_tx in close_tx_list:
                opened -= close_tx.quantity
            assert(opened >= 0)
            if opened == 0: continue

            for tx in following_tx_list:
                if open_tx.closed_by(tx):
                    sliced_tx = tx.remove(min(opened, tx.quantity))
                    close_tx_list.append(sliced_tx)
                    res = True
        return res

    def inventory(self):
        total = 0
        positions = {}
        first_date = datetime.max
        last_date = datetime.min
        for open_tx, close_tx_list in self.chains.items():
            opened = open_tx.quantity
            total += open_tx.amount
            symbol = open_tx.symbol
            self._ui = symbol.ui
            first_date = min(first_date, open_tx.date)
            last_date = max(first_date, open_tx.date)
            for close_tx in close_tx_list:
                opened -= close_tx.quantity
                total += close_tx.amount
                first_date = min(first_date, close_tx.date)
                last_date = max(first_date, close_tx.date)
            if opened != 0:
                symbol_str = open_tx.symbol.to_str()
                positions[symbol_str] = (positions.get(symbol_str, 0)
                                     + opened * (1 if open_tx.action == Action.BTO else -1))
        self._total = total
        self._positions = positions
        cost = self._cost = self._get_cost()
        assert(cost > 0)
        profit = self._profit = total + self._get_market_value()
        days = self._duration = (last_date.date() - first_date.date()).days + 1
        roi = profit / cost
        if profit > 0:
            if days < 365:
                roi = (1 + roi) ** (52 / math.ceil(days / 7)) - 1
            else:
                roi = math.exp(math.log(1 + roi) * (365 / days)) - 1
        self._roi = roi

    def _get_market_value(self):
        if not self._broker: return 0

        val = 0
        for symbol, qty in self.positions.items():
            price = self._broker.get_quotes(symbol)[symbol]
            val += price * qty * (100 if '_' in symbol else 1)
        return val

    def _get_cost(self):
        open_tx = self.chains.keys()
        options = [set(), set(), set(), set()]
        first_tx = next(iter(open_tx))
        for tx in open_tx:
            symbol = tx.symbol
            if not symbol.is_option(): continue

            index = (0 if tx.action == Action.BTO else 1)
            if symbol.type == InstrumentType.PUT:
                index += 2
            options[index].add(symbol.strike)

        if not any(options): return abs(first_tx.amount) # only stock
        
        if not (options[2] or options[3]): # only calls
            if not options[1]: return -first_tx.amount # only buy call
            if not options[0]: # only sell call
                return list(options[1])[0] * 100 * first_tx.quantity
            # assume short call spread
            return (list(options[0])[0] - list(options[1])[0]) * 100 * first_tx.quantity
        
        if not (options[0] or options[1]): # only puts
            if not options[3]: return -first_tx.amount # only buy put
            if not options[2]: # only sell put
                return list(options[3])[0] * 100 * first_tx.quantity
            # assume short put spread
            return (list(options[3])[0] - list(options[2])[0]) * 100 * first_tx.quantity

        # has calls and puts, assume short iron condor
        return (list(options[3])[0] - list(options[2])[0]) * 100 * first_tx.quantity

    def to_json(self):
        chains = []
        ui = None
        for otx, ctx in self._chains.items():
            tx = [otx.to_json(False)]
            tx.extend([tx.to_json(True) for tx in ctx])
            chains.append(tx)
            ui = otx.symbol.ui
        return {'ui': ui, 'total': self.total, 'profit': self.profit, 'chains': chains}

    @classmethod
    def from_doc(cls, doc):
        self = cls()
        self._total = doc['total']
        self._profit = doc['profit']
        self._cost = doc.get('cost', None)
        chains = self._chains = {}
        ui = doc['ui']
        for chain_array in doc['chains']:
            leading_tx = chain_array[0]
            leading_tx['ui'] = ui
            open_tx = Transaction.from_doc(chain_array[0])
            close_tx_list = []
            for tx in chain_array[1:]:
                tx['ui'] = ui
                tx['type'] = leading_tx['type']
                tx['strike'] = leading_tx.get('strike', None)
                tx['expired'] = leading_tx.get('expired', None)
                close_tx = Transaction.from_doc(tx)
                close_tx_list.append(close_tx)
            chains[open_tx] = close_tx_list
        return self

    @staticmethod
    def compute_total(tx_groups):
        total = 0
        profit = 0
        positions_list = {}
        for group in tx_groups:
            group.inventory()
            total += group.total
            profit += group.profit
            ui = group.ui
            if not positions_list.get(ui, None):
                positions_list[ui] = {}
            positions = positions_list[ui]
            for symbol, qty in group.positions.items():
                new_qty = positions.get(symbol, 0) + qty
                if new_qty:
                    positions[symbol] = new_qty
                else:
                    del positions[symbol]

        return total, profit, positions_list

    @property
    def chains(self):
        return self._chains

    @property
    def positions(self):
        return self._positions

    @property
    def ui(self):
        return self._ui

    @property
    def cost(self):
        return self._cost

    @property
    def profit(self):
        return self._profit

    @property
    def roi(self):
        return self._roi

    @property
    def total(self):
        return self._total

    @property
    def duration(self):
        return self._duration

    @property
    def completed(self):
        return not self.positions

    def __repr__(self):
        profit = "" if self.profit is None else f"profit={self.profit:.2f}"
        return f"TransationGroup: {profit}, {self._chains}"

    def __str__(self):
        return self.__repr__()
