# -*- coding: utf-8 -*-

from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader

from datetime import datetime
from pprint import pprint

def load_db(db_name, path, reload=True):
    loader = Loader(db_name)
    return loader.load(path, reload)

def total_cash(db_name, to_date=None):
    inspector = Inspector(db_name)
    if to_date:
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
    return inspector.total_cash(to_date)

def distinct_tickers(db_name, to_date=None):
    inspector = Inspector(db_name)
    if to_date:
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
    return inspector.distinct_tickers(to_date)

def ticker_costs(db_name, ticker, to_date=None):
    inspector = Inspector(db_name)
    if to_date:
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
    return inspector.ticker_costs(ticker, to_date)

def ticker_transaction_groups(db_name, ticker):
    inspector = Inspector(db_name)
    return inspector.ticker_transaction_groups(ticker)

def group_transactions(db_name, ticker, save_db=False):
    return Assembler(db_name).group_transactions(ticker, save_db)


if __name__ == '__main__':
    pprint("in cli")
