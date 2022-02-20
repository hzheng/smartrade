# -*- coding: utf-8 -*-

from smartrade.cli import ticker_transaction_groups, total_cash, distinct_tickers, ticker_costs, group_transactions
from smartrade.test.TestBase import TestBase

import unittest

class TestQuery(TestBase):

    expected_amounts = {
        '2022-02-07':
        {
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
        },
        '2022-02-14':
        {
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
    }

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

    def test_query_tickers(self):
        for date, expected_amt in self.expected_amounts.items():
            self.assertEqual(set(expected_amt.keys()),
                             set(distinct_tickers(self.DB_NAME, date)))

    def test_query_ticker(self):
        for date, expected_amt in self.expected_amounts.items():
            for ticker, amount in expected_amt.items():
                self.assertAlmostEqual(amount, ticker_costs(self.DB_NAME, ticker, date))

        self.assertAlmostEqual(0.00, ticker_costs(self.DB_NAME, 'NONE'))

    def test_group_transactions(self):
        twtr_tx = group_transactions(self.DB_NAME, 'TWTR')
        self.assertEqual(23, len(twtr_tx))
        self.assertEqual(4, len([tx for tx in twtr_tx if not tx.completed]))
        
        vmw_tx = group_transactions(self.DB_NAME, 'VMW')
        self.assertEqual(6, len(vmw_tx))
        self.assertEqual(0, len([tx for tx in vmw_tx if not tx.completed]))
        expected_profits = [38.40, 48.40, 75.70, 90.80, 91.70, 158.70]
        for i, profit in enumerate(sorted([tx.profit for tx in vmw_tx])):
            self.assertAlmostEqual(expected_profits[i], profit)
        
        for ticker in distinct_tickers(self.DB_NAME):
            tx = group_transactions(self.DB_NAME, ticker, True)
            self.assertTrue(tx)

        for ticker in distinct_tickers(self.DB_NAME):
            tx = group_transactions(self.DB_NAME, ticker)
            self.assertFalse(tx)

    def test_ticker_transaction_groups(self):
        fb_groups = ticker_transaction_groups(self.DB_NAME, 'FB')
        self.assertEqual(2, len(fb_groups))
        self.assertAlmostEqual(-1187.21, fb_groups[0].profit)


if __name__ == '__main__':
    unittest.main()
