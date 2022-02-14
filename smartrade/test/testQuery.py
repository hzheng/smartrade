# -*- coding: utf-8 -*-

from smartrade.cli import total_cash, distinct_ticks, tick_costs, group_transactions
from smartrade.test.TestBase import TestBase

import unittest

expected_amounts = {
        'SPY': -522.85,
        'QQQ': 26.80,
        'COIN': 81.24,
        'HOOD': -5826.32,
        'TWTR': -19909.64,
        'TSLA': 1353.32,
        'MSFT': 153.09,
        'AAPL': -191.54,
        'GOOG': 517.46,
        'INTC': -4770.01,
        'FB': -5307.86,
        'AMZN': 538.14,
        'TSM': 235.70,
        'QCOM': 351.70,
        'VMW': 503.70,
        'NVDA': -6300.65,
        'AMD': -4804.30,
        'GBTC': -811.61,
        'ETHE': -1005.96
}

class TestQuery(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_total_cash(self):
        self.assertAlmostEqual(0.00, total_cash(self.DB_NAME, '2021-12-31'))
        self.assertAlmostEqual(50977.48, total_cash(self.DB_NAME, '2022-01-01'))
        self.assertAlmostEqual(35893.74, total_cash(self.DB_NAME, '2022-01-30'))
        self.assertAlmostEqual(27995.65, total_cash(self.DB_NAME, '2022-02-04'))
        self.assertAlmostEqual(31094.92, total_cash(self.DB_NAME, '2022-02-07'))
        self.assertAlmostEqual(20593.13, total_cash(self.DB_NAME, '2022-02-14'))
        self.assertAlmostEqual(20593.13, total_cash(self.DB_NAME))

    def test_query_ticks(self):
        self.assertEqual(set(expected_amounts.keys()), set(distinct_ticks(self.DB_NAME)))

    def test_query_tick(self):
        for tick, amount in expected_amounts.items():
            self.assertAlmostEqual(amount, tick_costs(self.DB_NAME, tick))

        self.assertAlmostEqual(0.00, tick_costs(self.DB_NAME, 'NONE'))

    def test_group_transactions(self):
        twtr_tx = group_transactions(self.DB_NAME, 'TWTR')
        self.assertEqual(25, len(twtr_tx))
        self.assertEqual(4, len([tx for tx in twtr_tx if not tx.completed]))
        
        vmw_tx = group_transactions(self.DB_NAME, 'VMW')
        self.assertEqual(6, len(vmw_tx))
        self.assertEqual(0, len([tx for tx in vmw_tx if not tx.completed]))
        expected_profits = [38.40, 48.40, 75.70, 90.80, 91.70, 158.70]
        for i, profit in enumerate(sorted([tx.profit for tx in vmw_tx])):
            self.assertAlmostEqual(expected_profits[i], profit)


if __name__ == '__main__':
    unittest.main()
