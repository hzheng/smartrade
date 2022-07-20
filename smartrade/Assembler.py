# -*- coding: utf-8 -*-

from datetime import timedelta

from smartrade import app_logger
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import get_database, ASC, check

logger = app_logger.get_logger(__name__)

class Assembler:
    def __init__(self, db_name, account):
        db = get_database(db_name)
        self._tx_collection = db.transactions
        self._group_collection = db.transaction_groups
        self._account_cond = self.account_condition(account)

    @classmethod
    def account_condition(cls, account):
        return {'account' : account[-4:]}

    @classmethod
    def effective_condition(cls):
        unmerged_cond = {'$or':[{'merge_parent': None}, {'$expr':{'$eq':["$merge_parent", "$_id"]}}, {'$expr':{'$eq':["$merge_parent", "$slice_parent"]}}]}
        unsliced_cond = {'$expr':{'$ne':["$slice_parent", "$_id"]}}
        return {'$and': [unmerged_cond, unsliced_cond]}

    @classmethod
    def ineffective_condition(cls):
        merged_cond = {'$and':[{'merge_parent': {'$ne': None}}, {'$expr':{'$ne':["$merge_parent", "$_id"]}}, {'$expr':{'$ne':["$merge_parent", "$slice_parent"]}}]}
        sliced_cond = {'$expr':{'$eq':["$slice_parent", "$_id"]}}
        return {'$or': [merged_cond, sliced_cond]}

    @classmethod
    def virtual_condition(cls):
        sliced_cond = {'$expr':{'$ne':["$slice_parent", "$_id"]}}
        is_sliced_cond = {'$and': [sliced_cond, {'slice_parent': {'$ne': None}}]}
        merged_cond = {'$expr':{'$eq':["$merge_parent", "$_id"]}}
        return {'$or': [merged_cond, is_sliced_cond]}

    @classmethod
    def original_condition(cls):
        sliced_cond = {'$expr':{'$eq':["$slice_parent", "$_id"]}}
        is_sliced_cond = {'$or': [sliced_cond, {'slice_parent': {'$eq': None}}]}
        merged_cond = {'$expr':{'$ne':["$merge_parent", "$_id"]}}
        return {'$and': [merged_cond, is_sliced_cond]}

    def group_transactions(self, ticker, save_db=False):
        tx_collection = self._tx_collection
        effective_cond = self.effective_condition()
        ungrouped_cond = {**effective_cond, **self._account_cond, 'ui': ticker, 'grouped': {'$ne': True}, 'valid': 1}

        close_action_cond = {'action': {'$in': ['STC', 'BTC', 'SPLIT_FROM', 'EXPIRED', 'ASSIGNED', 'EXERCISE']},
                             **ungrouped_cond}
        following_dates = {res['date']
                           for res in tx_collection.find(close_action_cond, {'date': 1})}
        following_dates_before = {d - timedelta(seconds=1) for d in following_dates}
        following_dates_after = {d + timedelta(seconds=1) for d in following_dates}
        following_dates |= following_dates_before
        following_dates |= following_dates_after
        leading_cond = {**self._account_cond, 'action': {'$in': ['STO', 'BTO', 'SPLIT']},
                        'date': {'$nin': list(following_dates)},
                        **ungrouped_cond}
        following_cond = {**self._account_cond,
                          'action': {'$in': ['STC', 'BTC', 'EXPIRED', 'ASSIGNED', 'EXERCISE', 'STO', 'BTO', 'SPLIT', 'SPLIT_FROM', 'SPLIT_TO']},
                          'date': {'$in': list(following_dates)},
                          **ungrouped_cond}
        order = [('date', ASC), ('action', ASC), ('expired', ASC), ('strike', ASC), ('type', ASC)]

        leading_tx = tx_collection.find(leading_cond).sort(order)
        following_tx = tx_collection.find(following_cond).sort(order)
        groups, updated_tx_list, created_tx_map = TransactionGroup.assemble(leading_tx, following_tx)
        if save_db:
            incomplete = self._group_collection.delete_many({**self._account_cond, 'ui': ticker, 'completed': False})
            logger.debug("deleted %s incomplete transaction group(s)", incomplete.deleted_count)

        for tx in created_tx_map.values():
            check(tx.is_virtual() and tx.grouped is None, f"transaction {tx} should be virtual and not grouped")
            self._save(save_db, tx, False)
        for tx in updated_tx_list:
            check(tx.is_original(), f"transaction {tx} should be original")
            self._save(save_db, tx, True)
        for group in groups:
            for otx, ctx in group.chains.items():
                check(otx.is_effective(), f"transaction {otx} should be effective")
                update = self._was_created(otx, created_tx_map)
                otx.grouped = group.completed
                self._save(save_db, otx, update)
                for tx in ctx:
                    check(tx.is_effective(), f"transaction {tx} should be effective")
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
