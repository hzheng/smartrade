# -*- coding: utf-8 -*-

from smartrade import app
from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader

from flask import render_template
from os import listdir
from os.path import expanduser, dirname, abspath, join
from functools import reduce

from smartrade.TransactionGroup import TransactionGroup

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/list")
def list():
    db_name = app.config['database']
    inspector = Inspector(db_name)
    tickers = inspector.distinct_tickers()
    return render_template("tickers.html", tickers=tickers)

@app.route("/load")
def load():
    db_name = app.config['database']
    data_dir = app.config['data_dir']
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir) if f.endswith('.csv') or f.endswith('.json')])
    loader = Loader(db_name)
    for i, f in enumerate(data_files):
        loader.load(f, i == 0)
    assembler = Assembler(db_name)
    inspector = Inspector(db_name)
    tickers = inspector.distinct_tickers()
    for ticker in tickers:
        assembler.group_transactions(ticker, True)
    return render_template("tickers.html", tickers=tickers, loaded=True)

@app.route("/report/<ticker>")
def report(ticker):
    db_name = app.config['database']
    inspector = Inspector(db_name)
    ticker = ticker.upper()
    tx_groups = inspector.ticker_transaction_groups(ticker)
    total, profit, positions = TransactionGroup.compute_total(tx_groups)
    return render_template("transactions.html",
                           ticker=ticker, total=total, profit=profit,
                           positions=positions, groups=tx_groups)
