# -*- coding: utf-8 -*-

from smartrade.TransactionGroup import TransactionGroup

import pymongo

class Assembler:
    def __init__(self, db_name):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._transactions = self._db.transactions

    def group_transactions(self, tick, **criteria):
        tx = self._transactions
        outstanding_group_cond = {'ui': tick, 'grouped': False}
        close_action_cond = {'action': {'$in': ['STC', 'BTC', 'ASSIGNED']}}
        following_dates = {res['date'] for res in tx.find(
            {**close_action_cond, **outstanding_group_cond}, {'date': 1})}

        leading_cond = { 'action': {'$in': ['STO', 'BTO']}, 'date' : {'$nin': list(following_dates)} }

        order = [('date', pymongo.ASCENDING),
                 ('action', pymongo.ASCENDING),
                 ('expired', pymongo.ASCENDING),
                 ('strike', pymongo.ASCENDING),
                 ('type', pymongo.ASCENDING)]
        leading_tx = tx.find({**leading_cond, **outstanding_group_cond}).sort(order)

        following_cond = { 'action': {'$in': ['STC', 'BTC', 'ASSIGNED', 'STO', 'BTO']}, 'date' : {'$in': list(following_dates)} }
        following_tx = tx.find({**following_cond, **outstanding_group_cond}).sort(order)
        groups = TransactionGroup.assemble(leading_tx, following_tx)
        for group in groups:
            group.compute_profit()
            # TODO: write group to DB
        # TODO: update all grouped to True
        return groups

