# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction, Action, Symbol
from smartrade.TransactionGroup import TransactionGroup
from smartrade.test.TestBase import TestBase

import unittest


class TestTransaction(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_symbol(self):
        symbol_str = "TWTR 02/04/2022 38.00 C"
        symbol = Symbol(symbol_str)
        self.assertEqual(symbol_str, str(symbol))

        symbol_str = "HOOD_031122C14.5"
        symbol = Symbol(symbol_str)
        self.assertEqual(symbol_str, symbol.to_str())

    def test_transaction(self):
        transactions = [
            Transaction.from_dict(
                date="01/24/2022",
                price="$0.86",
                action="Sell to Open",
                fee="$6.60",
                quantity="10",
                amount="$853.40",
                symbol="AAPL 01/28/2022 140.00 P"),
            Transaction.from_dict(
                date="01/24/2022",
                price="$0.86",
                action="Sell to Open",
                fee="$13.20",
                quantity="20",
                amount="$1706.80",
                symbol="AAPL 01/28/2022 140.00 P"),
            Transaction.from_dict(
                date="01/24/2022",
                price="$0.54",
                action="Buy to Open",
                fee="$6.60",
                quantity="10",
                amount="-$546.60",
                symbol="AAPL 01/28/2022 135.00 P"),
            Transaction.from_dict(
                date="01/24/2022",
                price="$0.26",
                action="Sell to Open",
                fee="$6.60",
                quantity="10",
                amount="$253.40",
                symbol="SPY 02/04/2022 436.00 P"),
            Transaction.from_dict(
                date="01/24/2022",
                price="$0.26",
                action="Sell to Open",
                fee="$2.64",
                quantity="4",
                amount="$101.36",
                symbol="SPY 02/04/2022 436.00 P")
        ]
        tx = transactions[0].merge(transactions[1])
        self.assertEqual(Action.STO, tx.action)
        self.assertAlmostEqual(853.40 + 1706.80, tx.amount)
        tx = transactions[1].merge(transactions[2])
        self.assertIsNone(tx)
        tx = transactions[3].merge(transactions[4])
        self.assertAlmostEqual(253.40 + 101.36, tx.amount)

        merged_transactions = TransactionGroup.merge(transactions)
        self.assertEqual(3, len(merged_transactions))

        aapl_tx, spy_tx = TransactionGroup.combine(merged_transactions)
        self.assertEqual(2, len(aapl_tx))
        self.assertEqual(1, len(spy_tx))


if __name__ == '__main__':
    unittest.main()
