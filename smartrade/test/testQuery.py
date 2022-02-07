# -*- coding: utf-8 -*-

from smartrade.cli import query_total_cash, query_tick, query_ticks
import unittest

db_name = "trading_test"
expected_amounts = {
        'SPY': -522.85,
        'QQQ': 26.80,
        'COIN': 81.24,
        'HOOD': -10114.22,
        'TWTR': -16212.15,
        'TSLA': 1353.32,
        'MSFT': 259.47,
        'AAPL': -191.54,
        'GOOG': 443.07,
        'INTC': -9164.73,
        'FB': -4057.15,
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
        print("=====BEGIN {}=====".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("=====END {}=====".format(cls.__name__))

    def test_total_cash(self):
        self.assertAlmostEqual(50977.48, query_total_cash(db_name, '2022-01-01'))
        self.assertAlmostEqual(35893.74, query_total_cash(db_name, '2022-01-30'))
        self.assertAlmostEqual(27995.65, query_total_cash(db_name, '2022-02-04'))
        self.assertAlmostEqual(27995.65, query_total_cash(db_name))

    def test_query_ticks(self):
        self.assertEqual(set(expected_amounts.keys()), set(query_ticks(db_name)))

    def test_query_tick(self):
        for tick, amount in expected_amounts.items():
            self.assertAlmostEqual(amount, query_tick(db_name, tick))


if __name__ == '__main__':
    unittest.main()