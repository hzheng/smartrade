# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from dateutil.parser import parse

from smartrade import app_logger
from smartrade.Assembler import Assembler
from smartrade.Transaction import InstrumentType, Symbol, Transaction
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import check, get_database, ASC, DESC

logger = app_logger.get_logger(__name__)

class Inspector:
    def __init__(self, db_name, account, provider=None):
        db = get_database(db_name)
        self._provider = provider
        self._tx_collection = db.transactions
        self._group_collection = db.transaction_groups
        self._bal_collection = db.balance_history
        self._account_cond = Assembler.account_condition(account)
        self._valid_tx_cond = {**self._account_cond, 'valid': 1}
        self._effective_tx_cond = {**self._valid_tx_cond, **Assembler.effective_condition()}
        self._trading_tx_cond = {'action': {'$in': ['BTO', 'STO', 'STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE']}}

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
        return -self._total_amount(self._trading_tx_cond, start_date, end_date)

    def total_cash(self, start_date=None, end_date=None):
        return self._total_amount(None, start_date, end_date)

    def _total_amount(self, restrictions, start_date=None, end_date=None):
        amount = 'total_amount'
        condition = self._date_limit({**self._effective_tx_cond}, start_date, end_date)
        if restrictions:
            condition.update(restrictions)
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

    def summarize(self, include_quotes=True, start_date=None, end_date=None):
        total_market_value = 0
        total_profit = 0
        positions = {}
        for ticker in self.distinct_tickers(start_date, end_date):
            tx_groups = self.ticker_transaction_groups(ticker, include_quotes)
            total, profit, position, *_ = TransactionGroup.summarize(tx_groups, include_quotes)
            total_profit += profit
            total_market_value += profit - total
            positions.update(position)
        return total_profit, total_market_value, positions

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
    
    def ticker_transaction_groups(self, ticker, include_quotes=True):
        return [TransactionGroup.from_doc(doc, include_quotes) for doc in self._group_collection.find({**self._account_cond, 'ui': ticker})]
        # add start_date and end_date condition?
        #condition = self._date_limit({**self._account_cond, 'ui': ticker}, start_date, end_date)
        #return [TransactionGroup.from_doc(doc) for doc in self._group_collection.find(condition)]

    def positions(self, tickers=None, day=None):
        condition = self._date_limit({**self._effective_tx_cond, **self._trading_tx_cond}, None, day)
        if tickers:
            condition['ui'] = {'$in': tickers}
        positions = {}
        for tx in [Transaction.from_doc(doc) for doc in self._tx_collection.find(condition).sort([("date", ASC)])]:
            key = str(tx.symbol)
            if tx.symbol.type == InstrumentType.AUTO:
                key = key[:-1] + "C"
                if key not in positions:
                    key = key[:-1] + "P"
                    check(key in positions, f"key {key} should be in positions")
            bal = positions.get(key, 0)
            qty = tx.quantity * tx.position_sign(bal)
            positions[key] = bal + qty
        return {k : v for k, v in positions.items() if v != 0}

    def compute_balance(self, day=None):
        cash = self.total_cash(end_date=day)
        total_value = cash
        pos = self.positions(day=day)
        for symbol, quantity in pos.items():
            symbol_obj = Symbol(symbol)
            symbol_str = symbol_obj.to_str()
            price = self._provider.get_price(symbol_str, day)
            value = quantity * price * (100 if symbol_obj.is_option() else 1)
            total_value += value
        return (pos, cash, round(total_value, 2))
    
    def get_balance(self, day):
        day = datetime.combine(day.date(), datetime.min.time())
        cond = {**self._account_cond, 'date': day}
        for obj in self._bal_collection.find(cond):
            logger.debug("found saved balance %s", cond)
            return obj['balance'] 
        
        logger.debug("retrieving balance %s", cond)
        bal = self.compute_balance(day)[-1]
        self._bal_collection.insert_one({**cond, 'balance': bal})
        return bal

    def balance_history(self, start_date=None, end_date=None):
        first_tx_date, last_tx_date = self.transaction_period()
        if not start_date or start_date < first_tx_date:
            start_date = first_tx_date
        today = datetime.now()
        if not end_date or end_date > today:
            end_date = today
        if end_date > last_tx_date and not self.positions():
            end_date = last_tx_date
        start = datetime.combine(start_date.date(), datetime.max.time())
        end = datetime.combine(end_date.date(), datetime.max.time())
        logger.debug("getting balance history from %s to %s", start, end)
        delta = timedelta(days=1)
        res = {}
        while start <= end:
            bal = self.get_balance(start)
            res[start.strftime("%Y-%m-%d")] = bal #f"{bal:,.2f}"
            start += delta
        return res #dict(sorted(res.items()))