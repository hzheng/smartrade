# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.parser import parse

from smartrade.Assembler import Assembler
from smartrade.Transaction import Transaction
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import get_database, ASC, DESC


class Inspector:
    def __init__(self, db_name, account):
        db = get_database(db_name)
        self._tx_collection = db.transactions
        self._group_collection = db.transaction_groups
        self._account_cond = Assembler.account_condition(account)
        self._valid_tx_cond = {**self._account_cond, 'valid': 1}
        self._effective_tx_cond = {**self._valid_tx_cond, **Assembler.effective_condition()}
    
    def transaction_period(self):
        start_date = end_date = datetime.now()
        for obj in self._tx_collection.find(self._valid_tx_cond).sort([("date", ASC)]).limit(1):
            start_date = obj['date']
        for obj in self._tx_collection.find(self._valid_tx_cond).sort([("date", DESC)]).limit(1):
            end_date = obj['date']
        return (start_date, end_date)

    def total_investment(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['TRANSFER', 'JOURNAL']}}, start_date, end_date)

    def total_interest(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['INTEREST']}}, start_date, end_date)

    def total_dividend(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['DIVIDEND']}}, start_date, end_date)

    def total_trading(self, start_date=None, end_date=None):
        return -self._total_amount({'action':
                                    {'$in': ['BTO', 'STO', 'STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE']}},
                                   start_date, end_date)

    def total_cash(self, start_date=None, end_date=None):
        return self._total_amount(None, start_date, end_date)

    def _total_amount(self, restritions, start_date=None, end_date=None):
        amount = 'total_amount'
        condition = self._date_limit({**self._effective_tx_cond}, start_date, end_date)
        if restritions:
            condition.update(restritions)
        res = self._tx_collection.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def distinct_tickers(self, start_date=None, end_date=None):
        return self._tx_collection.distinct('ui', self._date_limit({**self._valid_tx_cond}, start_date, end_date))

    def ticker_costs(self, ticker, start_date=None, end_date=None):
        amount = 'total_amount'
        condition = self._date_limit({**self._effective_tx_cond, 'ui': ticker}, start_date, end_date)
        res = self._tx_collection.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def total_profit(self, start_date=None, end_date=None):
        total_market_value = 0
        total_profit = 0
        for ticker in self.distinct_tickers(start_date, end_date):
            tx_groups = self.ticker_transaction_groups(ticker)
            total, profit, *_ = TransactionGroup.summarize(tx_groups)
            total_profit += profit
            total_market_value += profit - total
        return total_profit, total_market_value

    def total_positions(self, start_date=None, end_date=None):
        tickers = self.distinct_tickers(start_date, end_date)
        positions = {}
        for ticker in tickers:
            tx_groups = self.ticker_transaction_groups(ticker)
            position = TransactionGroup.summarize(tx_groups)[2]
            positions.update(position)
        return positions

    def _date_limit(self, condition, start_date, end_date):
        date_limit = {}
        if end_date:
            if isinstance(end_date, str):
                end_date = parse(end_date)
            date_limit['$lte'] = end_date
        if start_date:
            if isinstance(start_date, str):
                start_date = parse(start_date)
            date_limit['$gte'] = start_date
        if date_limit:
            condition['date'] = date_limit
        return condition

    def transaction_list(self, start_date=None, end_date=None, ticker=None, asc=False,
                         valid=-2, grouped=-2, effective=-1, original=-1):
        cond = {**self._account_cond}
        if ticker:
            cond['ui'] = ticker.upper()
        if valid >= -1:
            cond['valid'] = valid
        if grouped == -1:
            cond['grouped'] = None
        elif grouped >= 0:
            cond['grouped'] = grouped > 0
        expr = None
        if effective >= 0:
            expr = Assembler.effective_condition() if effective else Assembler.ineffective_condition()
        if original >= 0:
            orig_expr = Assembler.original_condition() if original else Assembler.virtual_condition()
            if expr:
                expr = {'$and': [expr, orig_expr]}
            else:
                expr = orig_expr
        if expr:
            cond.update(expr)

        return [Transaction.from_doc(doc) for doc in self._tx_collection.find(
            self._date_limit(cond, start_date, end_date))
            .sort([("date", ASC if asc else DESC)])]

    def ticker_transactions(self, ticker):
        return [Transaction.from_doc(doc) for doc in self._tx_collection.find({**self._valid_tx_cond, 'ui': ticker})]
    
    def ticker_transaction_groups(self, ticker):
        TransactionGroup.clear_quotes(ticker)
        return [TransactionGroup.from_doc(doc) for doc in self._group_collection.find({**self._account_cond, 'ui': ticker})]
        # add start_date and end_date condition?
        #condition = self._date_limit({**self._account_cond, 'ui': ticker}, start_date, end_date)
        #return [TransactionGroup.from_doc(doc) for doc in self._group_collection.find(condition)]
