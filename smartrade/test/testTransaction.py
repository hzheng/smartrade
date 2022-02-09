# -*- coding: utf-8 -*-

from smartrade.Transaction import Transaction, Action
import unittest


class TestTransaction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=====BEGIN {}=====\n".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("\n=====END {}=====\n".format(cls.__name__))

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

        merged_transactions = Transaction.merge_transactions(transactions)
        self.assertEqual(3, len(merged_transactions))

        aapl_tx, spy_tx = Transaction.combine_open_transactions(merged_transactions)
        self.assertEqual(2, len(aapl_tx))
        self.assertEqual(1, len(spy_tx))

if __name__ == '__main__':
    unittest.main()
