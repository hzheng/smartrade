# -*- coding: utf-8 -*-

import unittest


class TestBase(unittest.TestCase):
    DB_NAME = "trading_test"
    ACCOUNT0 = "7379"
    ACCOUNT1 = "7977"

    @classmethod
    def setUpClass(cls):
        print(f"\n=====BEGIN {cls.__name__}=====\n")

    @classmethod
    def tearDownClass(cls):
        print(f"\n=====END {cls.__name__}=====\n")
