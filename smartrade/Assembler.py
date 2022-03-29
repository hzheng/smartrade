# -*- coding: utf-8 -*-

import pymongo

from smartrade import app_logger
from smartrade.TransactionGroup import TransactionGroup

logger = app_logger.get_logger(__name__)

class Assembler:
    def __init__(self, db_name, account):
        client = pymongo.MongoClient()
        self._db = client[db_name]
        self._tx_collection = self._db.transactions
        self._group_collection = self._db.transaction_groups
        self._account_cond = {'account' : account[-4:]}

    @classmethod
    def effective_condition(cls):
        unmerged_cond = {'$or':[{'merge_parent': None}, {'$expr':{'$eq':["$merge_parent", "$_id"]}}, {'$expr':{'$eq':["$merge_parent", "$slice_parent"]}}]}
        unsliced_cond = {'$expr':{'$ne':["$slice_parent", "$_id"]}}
        return {'$and': [unmerged_cond, unsliced_cond]}

    def group_transactions(self, ticker, save_db=False):
        tx_collection = self._tx_collection
        effective_cond = self.effective_condition()
        ungrouped_cond = {**effective_cond, **self._account_cond, 'ui': ticker, 'grouped': {'$ne': True}, 'valid': 1}

        close_action_cond = {'action': {'$in': ['STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE']},
                             **ungrouped_cond}
        following_dates = {res['date']
                           for res in tx_collection.find(close_action_cond, {'date': 1})}

        leading_cond = {**self._account_cond, 'action': {'$in': ['STO', 'BTO']},
                        'date': {'$nin': list(following_dates)},
                        **ungrouped_cond}
        following_cond = {**self._account_cond,
                          'action': {'$in': ['STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE', 'STO', 'BTO']},
                          'date': {'$in': list(following_dates)},
                          **ungrouped_cond}
        order = [('date', pymongo.ASCENDING),
                 ('action', pymongo.ASCENDING),
                 ('expired', pymongo.ASCENDING),
                 ('strike', pymongo.ASCENDING),
                 ('type', pymongo.ASCENDING)]

        leading_tx = tx_collection.find(leading_cond).sort(order)
        following_tx = tx_collection.find(following_cond).sort(order)
        groups, updated_tx_list, created_tx_map = TransactionGroup.assemble(leading_tx, following_tx)
        if save_db:
            incomplete = self._group_collection.delete_many({**self._account_cond, 'ui': ticker, 'completed': False})
            logger.debug("deleted %s incomplete transaction group(s)", incomplete.deleted_count)

        for tx in created_tx_map.values():
            assert(tx.is_virtual() and tx.grouped is None)
            self._save(save_db, tx, False)
        for tx in updated_tx_list:
            assert(tx.is_original())
            self._save(save_db, tx, True)
        for group in groups:
            for otx, ctx in group.chains.items():
                assert(otx.is_effective())
                update = self._was_created(otx, created_tx_map)
                otx.grouped = group.completed
                self._save(save_db, otx, update)
                for tx in ctx:
                    assert(tx.is_effective())
                    update = self._was_created(tx, created_tx_map)
                    tx.grouped = group.completed
                    self._save(save_db, tx, update)

            if save_db:
                self._group_collection.insert_one(group.to_json())
        return groups

    def _was_created(self, tx, created_tx_map):
        return tx.grouped is not None or tx.is_original() or (str(tx.id) in created_tx_map)

    def _save(self, save_db, tx, update):
        if not save_db: return
                
        tx_collection = self._tx_collection
        if update:
            logger.debug("updating transaction: %s", tx)
            tx_collection.update_one({'_id': tx.id},
                                     {'$set': {'merge_parent': tx.merge_parent, 'slice_parent': tx.slice_parent, 'grouped': tx.grouped}}, upsert=False)
        else:
            logger.debug("creating transaction: %s", tx)
            tx_collection.insert_one(tx.to_json())
