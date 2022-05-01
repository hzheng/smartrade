# -*- coding: utf-8 -*-

from os import listdir
from os.path import join
import datetime

from dateutil.parser import parse
from flask import render_template, redirect, request

from smartrade import app, app_logger
from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import check

logger = app_logger.get_logger(__name__)

@app.route("/")
def home():
    return redirect("/home")

@app.route("/home")
def account_home():
    account = request.args.get('account')
    if not request.args.get('ajax'):
        return render_template("home.html", init_account=account)

    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    total_profit, total_market_value = inspector.total_profit()
    total_cash = inspector.total_cash()
    total_market_value += total_cash
    summary = {
        'total_investment': inspector.total_investment(),
        'total_interest': inspector.total_interest(),
        'total_dividend': inspector.total_dividend(),
        'total_trading': inspector.total_trading(),
        'total_profit': total_profit,
        'total_market_value': total_market_value,
        'total_cash': total_cash
    }
    # avoid negative total_investment when calculating total profit rate
    summary['total_profit_rate'] = summary['total_profit'] / max(summary['total_investment'], 1)
    positions = inspector.total_positions()
    position_map = {symbol: qty for pos_map in positions.values() for symbol, qty in pos_map.items()}
    values=[{}, {}, 0, 0]
    symbols = position_map.keys()
    for symbol in symbols:
        quantity = position_map[symbol]
        index = 0
        price = TransactionGroup.get_price(symbol)
        value = quantity * price[0]
        if '_' in symbol:
            index = 1
            value *= 100
        values[index][symbol] = (quantity, price, value)
        values[index + 2] += value
    return {'summary': summary, 'values': values, 'period': inspector.transaction_period()}

@app.route("/load/<account>")
def load(account):
    db_name = app.config['DATABASE']
    data_dir = app.config['DATA_DIR']
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir)
                         if f.startswith(account) and (f.endswith('.csv') or f.endswith('.json'))])
    loader = Loader(db_name, account, app.config['broker'])
    load_scope = int(request.args.get('scope'))
    res = {'transactions': 0, 'transactionGroups': 0}
    if load_scope != 1: # load basic data
        for i, f in enumerate(data_files):
            loaded_tx = loader.load(f, i == 0)
            res['transactions'] += len(loaded_tx)
    if load_scope > 0: # load live data
        live_loaded_tx = loader.live_load(reload_all=(load_scope == 2))
        live_load_count = len(live_loaded_tx)
        if load_scope == 1 and live_load_count == 0: # no new data
            logger.info("no new transactions")
            return res
        res['transactions'] += live_load_count

    assembler = Assembler(db_name, account)
    inspector = Inspector(db_name, account)
    tickers = inspector.distinct_tickers()
    for ticker in tickers:
        created_tx_groups = assembler.group_transactions(ticker, True)
        res['transactionGroups'] += len(created_tx_groups)
    return res

@app.route("/transactionGroups")
def transaction_groups():
    account = request.args.get('account')
    ajax = request.args.get('ajax')
    if not ajax:
        return render_template("transaction_groups.html", init_account=account)

    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    if ajax == "1":
        return _get_transaction_info(inspector)

    ticker = request.args.get('ticker')
    tx_groups = inspector.ticker_transaction_groups(ticker)
    total, profit, positions, prices = TransactionGroup.summarize(tx_groups, True)
    return {
        'transactionGroups': [tx_group.to_json(True) for tx_group in tx_groups],
        'positions': positions,
        'prices': prices,
        'profit': profit,
        'total': total
    }

def _get_transaction_info(inspector):
        positions = {symbol: bool(pos) for symbol, pos in inspector.total_positions().items()}
        return {
            'period': inspector.transaction_period(),
            'positions': positions
        }

def _get_date_range(context):
    start_date = end_date = None
    date_range = request.args.get('dateRange')
    if date_range:
        start, end = date_range.split(",")
        if start:
            start_date = parse(start)
        if end:
            end_date = parse(end)
    logger.debug("%s: start_date=%s, end_date=%s", context, start_date, end_date)
    return start_date, end_date

@app.route("/transactions")
def transaction_history():
    account = request.args.get('account')
    ajax = request.args.get('ajax')
    if not ajax:
        return render_template("transaction_history.html", init_account=account)

    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    if ajax == "1":
        return _get_transaction_info(inspector)

    start_date, end_date = _get_date_range("transaction_history")
    order = request.args.get('dateOrder') or "0"
    ticker = request.args.get('ticker')
    valid = int(request.args.get('valid'))
    completed = int(request.args.get('completed'))
    effective = int(request.args.get('effective'))
    original = int(request.args.get('original'))
    transactions = inspector.transaction_list(start_date, end_date, ticker, order == "1",
                                              valid, completed, effective, original)

    total_cash = inspector.total_cash(start_date, end_date)
    end_cash = inspector.total_cash(None, end_date)
    start_cash = 0
    if start_date:
        start_cash = inspector.total_cash(None,  start_date - datetime.timedelta(0, 1))

    delta = end_cash - start_cash - total_cash
    logger.debug("start_cash=%s, end_cash=%s, total_cash=%s, (end_cash - start_cash - total_cash)=%s",
                 start_cash, end_cash, total_cash, delta)
    check(abs(delta) < 1e-5, f"delta {delta} should be small")
    return {
        'transactions': [tx.to_json(serialize=True) for tx in transactions],
        'cash': { 'start': start_cash, 'end': end_cash, 'total': total_cash }
    }

@app.errorhandler(Exception)
def server_error(err):
    logger.exception(err)
    return "Exception happened", 500
