# -*- coding: utf-8 -*-

from smartrade.cli import query_tick
import unittest


class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("=====BEGIN {}=====".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("=====END {}=====".format(cls.__name__))

    def test_query(self):
        db_name = "trading_test"
        self.assertAlmostEqual(-522.85, query_tick(db_name, 'SPY'))
        self.assertAlmostEqual(26.80, query_tick(db_name, 'QQQ'))
        self.assertAlmostEqual(81.24, query_tick(db_name, 'COIN'))
        self.assertAlmostEqual(-10114.22, query_tick(db_name, 'HOOD'))
        self.assertAlmostEqual(-7568.15, query_tick(db_name, 'TWTR'))
        self.assertAlmostEqual(1353.32, query_tick(db_name, 'TSLA'))
        self.assertAlmostEqual(259.47, query_tick(db_name, 'MSFT'))
        self.assertAlmostEqual(-191.54, query_tick(db_name, 'AAPL'))
        self.assertAlmostEqual(443.07, query_tick(db_name, 'GOOG'))
        self.assertAlmostEqual(-9164.73, query_tick(db_name, 'INTC'))
        self.assertAlmostEqual(-4057.15, query_tick(db_name, 'FB'))
        self.assertAlmostEqual(538.14, query_tick(db_name, 'AMZN'))
        self.assertAlmostEqual(235.70, query_tick(db_name, 'TSM'))
        self.assertAlmostEqual(351.70, query_tick(db_name, 'QCOM'))
        self.assertAlmostEqual(503.70, query_tick(db_name, 'VMW'))


if __name__ == '__main__':
    unittest.main()
