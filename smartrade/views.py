# -*- coding: utf-8 -*-

from os import listdir
from os.path import join

from flask import render_template

from smartrade import app
from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TransactionGroup import TransactionGroup
from smartrade.cli import total_investment

@app.route("/")
def index():
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name)
    total_investment = inspector.total_investment()
    total_interest = inspector.total_interest()
    total_cash = inspector.total_cash()
    return render_template("home.html", total_investment=total_investment,
                           total_interest=total_interest, total_cash=total_cash)

@app.route("/list")
def list():
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name)
    tickers = inspector.distinct_tickers()
    return render_template("tickers.html", tickers=tickers)

@app.route("/load")
def load():
    db_name = app.config['DATABASE']
    data_dir = app.config['DATA_DIR']
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
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name)
    ticker = ticker.upper()
    tx_groups = inspector.ticker_transaction_groups(ticker)
    total, profit, positions = TransactionGroup.compute_total(tx_groups)
    return render_template("transactions.html",
                           ticker=ticker, profit=profit,
                           positions=positions, groups=tx_groups)
