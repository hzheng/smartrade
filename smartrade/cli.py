# -*- coding: utf-8 -*-

from smartrade.Inspector import Inspector
from smartrade.Loader import Loader

from pprint import pprint

def load_db(db_name, path, reload=True):
    loader = Loader(db_name)
    return loader.load(path, reload)

def query_tick(db_name, tick):
    inspector = Inspector(db_name)
    result = inspector.query_tick(tick)
    total = 0
    for r in result:
        total += r.amount
    return total

if __name__ == '__main__':
    pprint("in cli")
