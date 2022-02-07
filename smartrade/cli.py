# -*- coding: utf-8 -*-

from smartrade.Inspector import Inspector
from smartrade.Loader import Loader

from datetime import datetime
from pprint import pprint

def load_db(db_name, path, reload=True):
    loader = Loader(db_name)
    return loader.load(path, reload)

def query_total_cash(db_name, to_date=None):
    inspector = Inspector(db_name)
    if to_date:
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
    return inspector.total_cash(to_date)

def query_ticks(db_name):
    inspector = Inspector(db_name)
    return inspector.distinct_ticks()

def query_tick(db_name, tick):
    inspector = Inspector(db_name)
    result = inspector.query_tick(tick)
    total = 0
    for r in result:
        total += r.amount
    return total

if __name__ == '__main__':
    pprint("in cli")
