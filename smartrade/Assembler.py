# -*- coding: utf-8 -*-

from smartrade.TransactionGroup import TransactionGroup

import pymongo


class Assembler:
    def __init__(self, db_name):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._tx_collection = self._db.transactions
        self._group_collection = self._db.transaction_groups

    def group_transactions(self, ticker, save_db=False):
        tx_collection = self._tx_collection
        ungrouped_cond = {'ui': ticker, 'grouped': False}
        close_action_cond = {'action': {'$in': ['STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE']},
                             **ungrouped_cond}
        following_dates = {res['date']
                           for res in tx_collection.find(close_action_cond, {'date': 1})}

        leading_cond = {'action': {'$in': ['STO', 'BTO']},
                        'date': {'$nin': list(following_dates)},
                        **ungrouped_cond}
        following_cond = {'action': {'$in': ['STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE', 'STO', 'BTO']},
                          'date': {'$in': list(following_dates)},
                          **ungrouped_cond}
        order = [('date', pymongo.ASCENDING),
                 ('action', pymongo.ASCENDING),
                 ('expired', pymongo.ASCENDING),
                 ('strike', pymongo.ASCENDING),
                 ('type', pymongo.ASCENDING)]

        leading_tx = tx_collection.find(leading_cond).sort(order)
        following_tx = tx_collection.find(following_cond).sort(order)
        groups = TransactionGroup.assemble(leading_tx, following_tx)
        for group in groups:
            if save_db:
                self._group_collection.insert_one(group.to_json())
        if save_db:
            tx_collection.update_many(leading_cond, {'$set': {'grouped': True}})
            tx_collection.update_many(following_cond, {'$set': {'grouped': True}})
        return groups
