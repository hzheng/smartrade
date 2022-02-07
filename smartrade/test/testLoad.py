# -*- coding: utf-8 -*-

from smartrade.cli import load_db
import unittest


class TestLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("=====BEGIN {}=====".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("=====END {}=====".format(cls.__name__))

    def test_load(self):
        valid_transactions, invalid_transactions = load_db("trading_test", "smartrade/test/sample1.csv")
        self.assertEqual(324, len(valid_transactions))
        self.assertEqual(2, len(invalid_transactions))


if __name__ == '__main__':
    unittest.main()