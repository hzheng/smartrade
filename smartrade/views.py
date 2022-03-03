# -*- coding: utf-8 -*-

from os import listdir
from os.path import join

from flask import render_template

from smartrade import app
from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TransactionGroup import TransactionGroup

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/home/<account>")
def account_home(account):
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
    provider = app.config['provider']
    positions = inspector.total_positions().values()
    position_map = {symbol: qty for pos_map in positions for symbol, qty in pos_map.items()}
    values=[{}, {}, 0, 0]
    quotes = provider.get_quotes(position_map.keys())
    for symbol, price in quotes.items():
        quantity = position_map[symbol]
        index = 0
        value = quantity * price
        if '_' in symbol:
            index = 1
            value *= 100
        values[index][symbol] = (quantity, price, value)
        values[index + 2] += value

    tickers = inspector.distinct_tickers()
    return render_template("home.html", account=account, summary=summary,
                           positions=positions, values=values, tickers=tickers,
                           period=inspector.transaction_period())

@app.route("/load/<account>")
def load(account):
    db_name = app.config['DATABASE']
    data_dir = app.config['DATA_DIR']
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir)
                         if f.startswith(account) and (f.endswith('.csv') or f.endswith('.json'))])
    loader = Loader(db_name, account, app.config['broker'])
    for i, f in enumerate(data_files):
        loader.load(f, i == 0)
    loader.live_load()
    assembler = Assembler(db_name, account)
    inspector = Inspector(db_name, account)
    tickers = inspector.distinct_tickers()
    for ticker in tickers:
        assembler.group_transactions(ticker, True)
    return render_template("tickers.html", account=account, tickers=tickers, loaded=True)

@app.route("/report/<account>/<ticker>")
def report(account, ticker):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    ticker = ticker.upper()
    tx_groups = inspector.ticker_transaction_groups(ticker)
    total, profit, positions = TransactionGroup.compute_total(tx_groups)
    return render_template("transactions.html",
                           account=account, ticker=ticker, profit=profit,
                           positions=positions, groups=tx_groups)

@app.route("/transactions/<account>")
def transaction_history(account):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    transactions = inspector.transaction_list()
    return render_template("transaction_history.html",
                           account=account, transactions=transactions)
