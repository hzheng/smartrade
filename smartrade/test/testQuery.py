# -*- coding: utf-8 -*-

from smartrade.cli import get_provider, distinct_tickers, get_config, group_transactions, \
    ticker_costs, ticker_transaction_groups, total_cash, total_dividend, total_interest, total_investment, total_trading
from smartrade.test.TestBase import TestBase
from smartrade.TransactionGroup import TransactionGroup

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
        config = get_config()
        TransactionGroup.set_provider(get_provider(config, cls.DB_NAME))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_total_amount(self):
        self.assertAlmostEqual(35893.74, total_cash(self.DB_NAME, self.ACCOUNT0, end_date='2022-01-30'))
        self.assertAlmostEqual(27995.65, total_cash(self.DB_NAME, self.ACCOUNT0, end_date='2022-02-04'))
        self.assertAlmostEqual(31094.92, total_cash(self.DB_NAME, self.ACCOUNT0, end_date='2022-02-07'))
        self.assertAlmostEqual(20593.13, total_cash(self.DB_NAME, self.ACCOUNT0, end_date='2022-02-14'))
        
        expected_values = {
            '2021-12-31': [0, 0, 0, 0, 0],
            '2022-01-01': [66282.48, 0, 0, 50977.48, 15305.00],
            '2022-02-23': [66282.48, 0.54, 0, 16652.41, 49630.61]
        }
        for (end_date, expected) in expected_values.items():
            self.assertAlmostEqual(expected[4], expected[0] + expected[1] + expected[2] - expected[3])
            self.assertAlmostEqual(expected[0], total_investment(self.DB_NAME, self.ACCOUNT0, end_date=end_date))
            self.assertAlmostEqual(expected[1], total_interest(self.DB_NAME, self.ACCOUNT0, end_date=end_date))
            self.assertAlmostEqual(expected[2], total_dividend(self.DB_NAME, self.ACCOUNT0, end_date=end_date))
            self.assertAlmostEqual(expected[3], total_cash(self.DB_NAME, self.ACCOUNT0, end_date=end_date))
            self.assertAlmostEqual(expected[4], total_trading(self.DB_NAME, self.ACCOUNT0, end_date=end_date))
            # self.assertAlmostEqual(expected[5], total_profit(self.DB_NAME, self.ACCOUNT0, end_date=end_date))

    def test_query_tickers(self):
        for date, expected_amt in self.expected_amounts.items():
            self.assertEqual(set(expected_amt.keys()),
                             set(distinct_tickers(self.DB_NAME, self.ACCOUNT0, end_date=date)))

    def test_query_ticker(self):
        for date, expected_amt in self.expected_amounts.items():
            for ticker, amount in expected_amt.items():
                self.assertAlmostEqual(amount, ticker_costs(self.DB_NAME, self.ACCOUNT0, ticker, end_date=date))

        self.assertAlmostEqual(0.00, ticker_costs(self.DB_NAME, self.ACCOUNT0, 'NONE'))

    def test_group_transactions(self):
        twtr_tx = group_transactions(self.DB_NAME, self.ACCOUNT0, 'TWTR')
        self.assertEqual(23, len(twtr_tx))
        self.assertEqual(4, len([tx for tx in twtr_tx if not tx.completed]))
        
        vmw_tx = group_transactions(self.DB_NAME, self.ACCOUNT0, 'VMW')
        self.assertEqual(6, len(vmw_tx))
        self.assertEqual(0, len([tx for tx in vmw_tx if not tx.completed]))
        expected_profits = [38.40, 48.40, 75.70, 90.80, 91.70, 158.70]
        for i, profit in enumerate(sorted([tx.profit for tx in vmw_tx])):
            self.assertAlmostEqual(expected_profits[i], profit)
        
        for ticker in distinct_tickers(self.DB_NAME, self.ACCOUNT0):
            tx = group_transactions(self.DB_NAME, self.ACCOUNT0, ticker, True)
            self.assertTrue(tx)

        # for ticker in distinct_tickers(self.DB_NAME, self.ACCOUNT0):
            # tx = group_transactions(self.DB_NAME, self.ACCOUNT0, ticker)
            # self.assertFalse(tx) # may still have incomplete groups!

    def test_ticker_transaction_groups(self):
        fb_groups = ticker_transaction_groups(self.DB_NAME, self.ACCOUNT0, 'FB')
        self.assertEqual(2, len(fb_groups))
        # self.assertAlmostEqual(-1940.65, fb_groups[0].profit) # not completed yet
        self.assertAlmostEqual(-1187.21, fb_groups[1].profit)
        total, profit, position_list, _ = TransactionGroup.summarize(fb_groups)
        self.assertAlmostEqual(-5307.86, total)
        self.assertEqual(1, len(position_list['FB']))

        twtr_groups = ticker_transaction_groups(self.DB_NAME, self.ACCOUNT0, 'TWTR')
        self.assertEqual(23, len(twtr_groups))
        total, profit, position_list, _ = TransactionGroup.summarize(twtr_groups)
        self.assertAlmostEqual(-19909.64, total)
        self.assertEqual(2, len(position_list['TWTR']))
        
        nvda_groups = ticker_transaction_groups(self.DB_NAME, self.ACCOUNT0, 'NVDA')
        total, profit, position_list, _ = TransactionGroup.summarize(nvda_groups)
        self.assertEqual(2, len(position_list['NVDA']))
        self.assertAlmostEqual(-12651.31, total)


if __name__ == '__main__':
    unittest.main()
