# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction, Action

from collections import deque

class TransactionGroup:

    def __init__(self, leading_transactions=None):
        self._chains = {tx: [] for tx in leading_transactions} if leading_transactions else {}
        self._positions = None
        self._cost = None
        self._profit = None
        self._total = None
        self._ui = None

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
        for open_tx, close_tx_list in self._chains.items():
            opened = open_tx.quantity
            total += open_tx.amount
            symbol = open_tx.symbol
            self._ui = symbol.ui
            for close_transaction in close_tx_list:
                opened -= close_transaction.quantity
                total += close_transaction.amount
            if opened != 0:
                symbol_str = str(open_tx.symbol)
                positions[symbol_str] = (positions.get(symbol_str, 0)
                                     + opened * (1 if open_tx.action == Action.BTO else -1))
        self._total = total
        self._profit = None if positions else total
        self._positions = positions
        # TODO: calculate cost

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
        completed = True
        positions_list = {}
        for group in tx_groups:
            group.inventory()
            if group.profit is None:
                completed = False
            total += group.total
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

        profit = total if completed else None
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
    def total(self):
        return self._total

    @property
    def completed(self):
        return self._profit is not None

    def __repr__(self):
        profit = "" if self.profit is None else f"profit={self.profit:.2f}"
        return f"TransationGroup: {profit}, {self._chains}"

    def __str__(self):
        return self.__repr__()
