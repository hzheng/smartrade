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
        transactions = load_db(self.DB_NAME, self.ACCOUNT0, f"smartrade/test/{self.ACCOUNT0}-1.csv")
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(347, len(valid_transactions))
        self.assertEqual(2, len(invalid_transactions))
 
        transactions = load_db(self.DB_NAME, self.ACCOUNT0, f"smartrade/test/{self.ACCOUNT0}-2.csv", False)
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(29, len(valid_transactions))
        self.assertEqual(2, len(invalid_transactions))
 
        transactions = load_db(self.DB_NAME, self.ACCOUNT0, f"smartrade/test/{self.ACCOUNT0}-3.json", False)
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(6, len(valid_transactions))
        self.assertEqual(4, len(invalid_transactions))
 
        transactions = load_db(self.DB_NAME, self.ACCOUNT1, f"smartrade/test/{self.ACCOUNT1}-1.csv", True)
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(10, len(valid_transactions))
        self.assertEqual(2, len(invalid_transactions))
 
        transactions = load_db(self.DB_NAME, self.ACCOUNT1, f"smartrade/test/{self.ACCOUNT1}-2.json", False)
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(5, len(valid_transactions))
        self.assertEqual(6, len(invalid_transactions))
 
        transactions = load_db(self.DB_NAME, self.ACCOUNT2, f"smartrade/test/{self.ACCOUNT2}-1.csv", True)
        valid_transactions = [tx for tx in transactions if tx.valid == 1]
        invalid_transactions = [tx for tx in transactions if tx.valid <= 0]
        self.assertEqual(23, len(valid_transactions))
        self.assertEqual(5, len(invalid_transactions))


if __name__ == '__main__':
    unittest.main()
