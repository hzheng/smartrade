# -*- coding: utf-8 -*-

import json
import os

from smartrade.CryptoTransaction import CryptoTransaction, CryptoAction
from smartrade.CryptoLoader import CryptoLoader
from smartrade.test.TestBase import TestBase

import unittest

NEED_PRINT = False


class TestCrypto(TestBase):
    ERROR_PLACES  = 7
    DATA_DIR = None

    def setUp(self):
        super().setUp()
        data_dir_var = "TRADE_DATA"
        self.DATA_DIR = os.getenv(data_dir_var)
        assert self.DATA_DIR, f"please set environment variable {data_dir_var}"

    def check(self, transactions, symbols, expected_result, include_transfer=False, need_print=True):
        total_actual_cost = 0
        total_fifo_pnl = 0
        total_fifo_cost = 0
        total_fifo_proceeds = 0
        total_fifo_latest_cost = 0
        total_lifo_pnl = 0
        total_lifo_cost = 0
        total_lifo_proceeds = 0
        total_lifo_latest_cost = 0
        total_hifo_pnl = 0
        total_hifo_cost = 0
        total_hifo_proceeds = 0
        total_hifo_latest_cost = 0
        for symbol in sorted(symbols):
            expected = expected_result.get(symbol, None)
            tx_list = [tx for tx in transactions if tx.symbol == symbol]
            actual_cost = 0
            position = 0
            for tx in tx_list:
                position += tx.quantity
                if tx.action != CryptoAction.TRANSFER:
                    actual_cost += tx.amount
            total_actual_cost += actual_cost
            if need_print:
                print("----------", symbol, "----------")
                print("actual cost =", actual_cost, "actual position =", position)

            self.assertAlmostEqual(expected['actual_cost'], actual_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} actual_cost {actual_cost} should be {expected['actual_cost']}")
            self.assertAlmostEqual(expected['actual_position'], position, self.ERROR_PLACES,
                                   f"symbol {symbol} actual_position {position} should be {expected['actual_position']}")

            if symbol == 'USD': continue

            last_pnl, last_cost, last_proceeds, last_latest_cost, last_pos = CryptoTransaction.get_pnl_from_last(
                tx_list, include_transfer)
            fifo_pnl, fifo_cost, fifo_proceeds, fifo_latest_cost, fifo_pos = CryptoTransaction.get_pnl(
                tx_list, 1, include_transfer)
            lifo_pnl, lifo_cost, lifo_proceeds, lifo_latest_cost, lifo_pos = CryptoTransaction.get_pnl(
                tx_list, -1, include_transfer)
            hifo_pnl, hifo_cost, hifo_proceeds, hifo_latest_cost, hifo_pos = CryptoTransaction.get_pnl(
                tx_list, 0, include_transfer)

            # check get_pnl_from_last == get_pnl(fifo)
            self.assertAlmostEqual(last_pnl, fifo_pnl)
            self.assertAlmostEqual(last_cost, fifo_cost)
            self.assertAlmostEqual(last_proceeds, fifo_proceeds)
            self.assertAlmostEqual(last_latest_cost, fifo_latest_cost)
            self.assertAlmostEqual(last_pos, fifo_pos)

            # check all positions are the same
            self.assertAlmostEqual(fifo_pos, lifo_pos)
            self.assertAlmostEqual(fifo_pos, hifo_pos)

            # check pnl == cost + proceeds
            self.assertAlmostEqual(fifo_pnl, fifo_cost + fifo_proceeds)
            self.assertAlmostEqual(lifo_pnl, lifo_cost + lifo_proceeds)
            self.assertAlmostEqual(hifo_pnl, hifo_cost + hifo_proceeds)

            # check pnl == actual_cost - latest_cost
            self.assertAlmostEqual(fifo_pnl, actual_cost - fifo_latest_cost)
            self.assertAlmostEqual(lifo_pnl, actual_cost - lifo_latest_cost)
            self.assertAlmostEqual(hifo_pnl, actual_cost - hifo_latest_cost)

            if need_print:
                print("position =", fifo_pos)
            self.assertAlmostEqual(expected['position'], fifo_pos, self.ERROR_PLACES,
                                   f"symbol {symbol} position {fifo_pos} should be {expected['position']}")

            if need_print:
                print("fifo pnl =", fifo_pnl, "cost =", fifo_cost, "fifo_proceeds =",
                      fifo_proceeds, "latest_cost =", fifo_latest_cost)
                print("lifo pnl =", lifo_pnl, "cost =", lifo_cost, "lifo_proceeds =",
                      lifo_proceeds, "latest_cost =", lifo_latest_cost)
                print("hifo pnl =", hifo_pnl, "cost =", hifo_cost, "hifo_proceeds =",
                      hifo_proceeds, "latest_cost =", hifo_latest_cost)
            self.assertAlmostEqual(expected['fifo_pnl'], fifo_pnl, self.ERROR_PLACES,
                                   f"symbol {symbol} fifo_pnl {fifo_pnl} should be {expected['fifo_pnl']}")
            self.assertAlmostEqual(expected['fifo_cost'], fifo_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} fifo_cost {fifo_cost} should be {expected['fifo_cost']}")
            self.assertAlmostEqual(expected['fifo_proceeds'], fifo_proceeds, self.ERROR_PLACES,
                                   f"symbol {symbol} fifo_proceeds {fifo_proceeds} should be {expected['fifo_proceeds']}")
            self.assertAlmostEqual(expected['fifo_latest_cost'], fifo_latest_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} fifo_latest_cost {fifo_latest_cost} should be {expected['fifo_latest_cost']}")

            self.assertAlmostEqual(expected['lifo_pnl'], lifo_pnl, self.ERROR_PLACES,
                                   f"symbol {symbol} lifo_pnl {lifo_pnl} should be {expected['lifo_pnl']}")
            self.assertAlmostEqual(expected['lifo_cost'], lifo_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} lifo_cost {lifo_cost} should be {expected['lifo_cost']}")
            self.assertAlmostEqual(expected['lifo_proceeds'], lifo_proceeds, self.ERROR_PLACES,
                                   f"symbol {symbol} lifo_proceeds {lifo_proceeds} should be {expected['lifo_proceeds']}")
            self.assertAlmostEqual(expected['lifo_latest_cost'], lifo_latest_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} lifo_latest_cost {lifo_latest_cost} should be {expected['lifo_latest_cost']}")

            self.assertAlmostEqual(expected['hifo_pnl'], hifo_pnl, self.ERROR_PLACES,
                                   f"symbol {symbol} hifo_pnl {hifo_pnl} should be {expected['hifo_pnl']}")
            self.assertAlmostEqual(expected['hifo_cost'], hifo_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} hifo_cost {hifo_cost} should be {expected['hifo_cost']}")
            self.assertAlmostEqual(expected['hifo_proceeds'], hifo_proceeds, self.ERROR_PLACES,
                                   f"symbol {symbol} hifo_proceeds {hifo_proceeds} should be {expected['hifo_proceeds']}")
            self.assertAlmostEqual(expected['hifo_latest_cost'], hifo_latest_cost, self.ERROR_PLACES,
                                   f"symbol {symbol} hifo_latest_cost {hifo_latest_cost} should be {expected['hifo_latest_cost']}")

            total_fifo_pnl += fifo_pnl
            total_fifo_cost += fifo_cost
            total_fifo_proceeds += fifo_proceeds
            total_fifo_latest_cost += fifo_latest_cost

            total_lifo_pnl += lifo_pnl
            total_lifo_cost += lifo_cost
            total_lifo_proceeds += lifo_proceeds
            total_lifo_latest_cost += lifo_latest_cost

            total_hifo_pnl += hifo_pnl
            total_hifo_cost += hifo_cost
            total_hifo_proceeds += hifo_proceeds
            total_hifo_latest_cost += hifo_latest_cost

        self.assertAlmostEqual(
            total_fifo_pnl, total_actual_cost - total_fifo_latest_cost)
        self.assertAlmostEqual(
            total_lifo_pnl, total_actual_cost - total_lifo_latest_cost)
        self.assertAlmostEqual(
            total_hifo_pnl, total_actual_cost - total_hifo_latest_cost)

        self.assertAlmostEqual(
            total_fifo_pnl, total_fifo_cost + total_fifo_proceeds)
        self.assertAlmostEqual(
            total_lifo_pnl, total_lifo_cost + total_lifo_proceeds)
        self.assertAlmostEqual(
            total_hifo_pnl, total_hifo_cost + total_hifo_proceeds)

        if need_print:
            print("=========================")
            print("total actual cost =", total_actual_cost)
            print("total_fifo_pnl =", total_fifo_pnl, "total_fifo_cost =", total_fifo_cost,
                  "total_fifo_proceeds =", total_fifo_proceeds,
                  "total_fifo_latest_cost =", total_fifo_latest_cost)
            print("total_lifo_pnl =", total_lifo_pnl, "total_lifo_cost =", total_lifo_cost,
                  "total_lifo_proceeds =", total_lifo_proceeds,
                  "total_lifo_latest_cost =", total_lifo_latest_cost)
            print("total_hifo_pnl =", total_hifo_pnl, "total_hifo_cost =", total_hifo_cost,
                  "total_hifo_proceeds =", total_hifo_proceeds,
                  "total_hifo_latest_cost =", total_hifo_latest_cost)

        self.assertAlmostEqual(
            expected_result['total_actual_cost'], total_actual_cost)
        self.assertAlmostEqual(
            expected_result['total_fifo_pnl'], total_fifo_pnl)
        self.assertAlmostEqual(
            expected_result['total_fifo_cost'], total_fifo_cost)
        self.assertAlmostEqual(
            expected_result['total_fifo_proceeds'], total_fifo_proceeds)
        self.assertAlmostEqual(
            expected_result['total_fifo_latest_cost'], total_fifo_latest_cost)
        self.assertAlmostEqual(
            expected_result['total_lifo_pnl'], total_lifo_pnl)
        self.assertAlmostEqual(
            expected_result['total_lifo_cost'], total_lifo_cost)
        self.assertAlmostEqual(
            expected_result['total_lifo_proceeds'], total_lifo_proceeds)
        self.assertAlmostEqual(
            expected_result['total_lifo_latest_cost'], total_lifo_latest_cost)
        self.assertAlmostEqual(
            expected_result['total_hifo_pnl'], total_hifo_pnl)
        self.assertAlmostEqual(
            expected_result['total_hifo_cost'], total_hifo_cost)
        self.assertAlmostEqual(
            expected_result['total_hifo_proceeds'], total_hifo_proceeds)
        self.assertAlmostEqual(
            expected_result['total_hifo_latest_cost'], total_hifo_latest_cost)

    def test_coinbase1(self):
        loader = CryptoLoader()
        transactions, symbols = loader.load(self.DATA_DIR + "/coinbase1.csv", 'coinbase')
        with open(self.DATA_DIR + "/summary/coinbase1.json") as json_file:
            expected = json.load(json_file)
        self.check(transactions, symbols, expected, need_print=NEED_PRINT)

    def test_coinbase2(self):
        loader = CryptoLoader()
        transactions, symbols = loader.load(self.DATA_DIR + "/coinbase2.csv", 'coinbase')
        with open(self.DATA_DIR + "/summary/coinbase2.json") as json_file:
            expected = json.load(json_file)
        self.check(transactions, symbols, expected, need_print=NEED_PRINT)

    def test_gemini1(self):
        loader = CryptoLoader()
        # coins from coinbase are transferred to gemini
        transactions, symbols = loader.load(self.DATA_DIR + "/coinbase2.csv", 'coinbase')
        # ignore transfer from coinbase to gemini as if they were transacted in gemini
        transactions = [ tx for tx in transactions if tx.action != CryptoAction.TRANSFER]
        transactions2, symbols = loader.load(self.DATA_DIR + "/gemini1.csv", 'gemini')
        transactions.extend(transactions2)
        with open(self.DATA_DIR + "/summary/gemini1.json") as json_file:
            expected = json.load(json_file)
        self.check(transactions, symbols, expected, include_transfer=False, need_print=NEED_PRINT)


if __name__ == '__main__':
    unittest.main()
