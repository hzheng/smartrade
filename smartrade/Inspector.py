# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.parser import parse
import pymongo

from smartrade.Transaction import Transaction
from smartrade.TransactionGroup import TransactionGroup


class Inspector:
    def __init__(self, db_name):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._tx_collection = self._db.transactions
        self._group_collection = self._db.transaction_groups
    
    def transaction_period(self, account_alias=None):
        start_date = end_date = datetime.now()
        for obj in self._db.transactions.find().sort([("date", pymongo.ASCENDING)]).limit(1):
            start_date = obj['date']
        for obj in self._db.transactions.find().sort([("date", pymongo.DESCENDING)]).limit(1):
            end_date = obj['date']
        return (start_date, end_date)

    def total_investment(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['TRANSFER']}}, start_date, end_date)

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
        condition = self._date_limit({}, start_date, end_date)
        if restritions:
            condition.update(restritions)
        res = self._tx_collection.aggregate(
            [{'$match': condition},
             {'$group': {'_id': None, amount: {'$sum': "$amount"}}}])
        for r in res:
            return r[amount]
        return 0.0

    def distinct_tickers(self, start_date=None, end_date=None):
        return self._tx_collection.distinct('ui', self._date_limit({}, start_date, end_date))

    def ticker_costs(self, ticker, start_date=None, end_date=None):
        amount = 'total_amount'
        condition = self._date_limit({'ui': ticker}, start_date, end_date)
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
            total, profit, _ = TransactionGroup.compute_total(tx_groups)
            total_profit += profit
            total_market_value += profit - total
        return total_profit, total_market_value

    def total_positions(self, start_date=None, end_date=None):
        tickers = self.distinct_tickers(start_date, end_date)
        positions = {}
        for ticker in tickers:
            tx_groups = self.ticker_transaction_groups(ticker)
            *_, position = TransactionGroup.compute_total(tx_groups)
            positions.update(position)
        return positions

    @staticmethod
    def _date_limit(condition, start_date, end_date):
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

    def ticker_transactions(self, ticker):
        return [Transaction.from_doc(doc) for doc in self._tx_collection.find({'ui': ticker})]
    
    def ticker_transaction_groups(self, ticker):
        return [TransactionGroup.from_doc(doc) for doc in self._group_collection.find({'ui': ticker})]
