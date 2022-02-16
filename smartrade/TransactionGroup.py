# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction

from collections import deque

class TransactionGroup:

    def __init__(self, leading_transactions):
        self._combo = {tx: [] for tx in leading_transactions}
        self._cost = None
        self._profit = None

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
                        group._combo[tx] = []
                    following_tx_queue.appendleft(close_tx_list)
                    grouped = True
                    break
            assert(grouped)
        return groups
    
    def _followed_by(self, following_tx_list):
        res = False
        for open_tx, close_tx_list in self._combo.items():
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

    def compute_profit(self):
        amount = 0
        for open_tx, close_tx_list in self._combo.items():
            opened = open_tx.quantity
            amount += open_tx.amount
            for close_transaction in close_tx_list:
                opened -= close_transaction.quantity
                amount += close_transaction.amount
            if opened != 0:
                return

        self._profit = amount
        # TODO: calculate cost

    def to_json(self):
        combo = []
        ui = None
        for otx, ctx in self._combo.items():
            tx = [otx.to_json(False)]
            tx.extend([tx.to_json(True) for tx in ctx])
            combo.append(tx)
            ui = otx.symbol.ui
        return {'ui': ui, 'profit': self.profit, 'combo': combo}

    @property
    def cost(self):
        return self._cost

    @property
    def profit(self):
        return self._profit

    @property
    def completed(self):
        return self._profit is not None

    def __repr__(self):
        profit = "" if self.profit is None else f"profit={self.profit:.2f}"
        return f"TransationGroup: {profit}, {self._combo}"

    def __str__(self):
        return self.__repr__()
