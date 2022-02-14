# -*- coding: utf-8 -*-

from smartrade.cli import total_cash, distinct_ticks, tick_costs, group_transactions
import unittest

db_name = "trading_test"
expected_amounts = {
        'SPY': -522.85,
        'QQQ': 26.80,
        'COIN': 81.24,
        'HOOD': -5764.24,
        'TWTR': -16212.15,
        'TSLA': 1353.32,
        'MSFT': 259.47,
        'AAPL': -191.54,
        'GOOG': 443.07,
        'INTC': -9164.73,
        'FB': -5307.86,
        'AMZN': 538.14,
        'TSM': 235.70,
        'QCOM': 351.70,
        'VMW': 503.70,
        'GBTC': -811.61,
        'ETHE': -1005.96
}

class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=====BEGIN {}=====\n".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("\n=====END {}=====\n".format(cls.__name__))

    def test_total_cash(self):
        self.assertAlmostEqual(0.00, total_cash(db_name, '2021-12-31'))
        self.assertAlmostEqual(50977.48, total_cash(db_name, '2022-01-01'))
        self.assertAlmostEqual(35893.74, total_cash(db_name, '2022-01-30'))
        self.assertAlmostEqual(27995.65, total_cash(db_name, '2022-02-04'))
        self.assertAlmostEqual(31094.92, total_cash(db_name, '2022-02-07'))
        self.assertAlmostEqual(31094.92, total_cash(db_name))

    def test_query_ticks(self):
        self.assertEqual(set(expected_amounts.keys()), set(distinct_ticks(db_name)))

    def test_query_tick(self):
        for tick, amount in expected_amounts.items():
            self.assertAlmostEqual(amount, tick_costs(db_name, tick))

        self.assertAlmostEqual(0.00, tick_costs(db_name, 'NONE'))

    def test_group_transactions(self):
        twtr_tx = group_transactions(db_name, 'TWTR')
        self.assertEqual(22, len(twtr_tx))
        self.assertEqual(6, len([tx for tx in twtr_tx if not tx.completed]))
        
        vmw_tx = group_transactions(db_name, 'VMW')
        self.assertEqual(6, len(vmw_tx))
        self.assertEqual(0, len([tx for tx in vmw_tx if not tx.completed]))
        expected_profits = [38.40, 48.40, 75.70, 90.80, 91.70, 158.70]
        for i, profit in enumerate(sorted([tx.profit for tx in vmw_tx])):
            self.assertAlmostEqual(expected_profits[i], profit)


if __name__ == '__main__':
    unittest.main()
