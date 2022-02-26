# -*- coding: utf-8 -*-

from smartrade.cli import load_db
from smartrade.test.TestBase import TestBase

import unittest


class TestLoad(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_load(self):
        valid_transactions, invalid_transactions = load_db(self.DB_NAME, "smartrade/test/sample1.csv")
        self.assertEqual(347, len(valid_transactions))
        self.assertEqual(3, len(invalid_transactions))
 
        valid_transactions, invalid_transactions = load_db(self.DB_NAME, "smartrade/test/sample2.csv", False)
        self.assertEqual(27, len(valid_transactions))
        self.assertEqual(3, len(invalid_transactions))
 
        valid_transactions, invalid_transactions = load_db(self.DB_NAME, "smartrade/test/sample3.json", False)
        self.assertEqual(6, len(valid_transactions))
        self.assertEqual(0, len(invalid_transactions))


if __name__ == '__main__':
    unittest.main()
