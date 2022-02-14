# -*- coding: utf-8 -*-

import unittest


class TestBase(unittest.TestCase):
    DB_NAME = "trading_test"

    @classmethod
    def setUpClass(cls):
        print("\n=====BEGIN {}=====\n".format(cls.__name__))

    @classmethod
    def tearDownClass(cls):
        print("\n=====END {}=====\n".format(cls.__name__))
