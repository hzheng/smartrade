# -*- coding: utf-8 -*-

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

    def total_investment(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['TRANSFER']}}, start_date, end_date)

    def total_interest(self, start_date=None, end_date=None):
        return self._total_amount({'action': {'$in': ['INTEREST']}}, start_date, end_date)

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
