# -*- coding: utf-8 -*-

from flask import jsonify, render_template, session

from smartrade import app, app_logger
from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import check, to_json

logger = app_logger.get_logger(__name__)

@app.route("/")
def index():
    accounts = app.config['broker_client'][0]['accounts']
    default_account = list(accounts[0].values())[0][-4:] #TODO: get from login
    session['default_account'] = default_account
    return render_template('index.html')

@app.route('/account/<account>/summary', methods=['GET'])
def account_summary(account):
    db_name = app.config['DATABASE']
    provider = app.config['provider']
    inspector = Inspector(db_name, account, provider)
    total_profit, total_market_value, positions = inspector.summarize(False)
    total_cash = inspector.total_cash()
    total_market_value += total_cash
    position_map = {symbol: qty for pos_map in positions.values() for symbol, qty in pos_map.items()}
    symbols = position_map.keys()
    for symbol in symbols:
        quantity = position_map[symbol]
        price = provider.get_price(symbol)
        value = quantity * price
        if '_' in symbol:
            value *= 100
        total_market_value += value
        total_profit += value
    total_dividend = inspector.total_dividend()
    total_interest = inspector.total_interest()
    total_profit += total_dividend + total_interest
    summary = {
        'total_investment': inspector.total_investment(),
        'total_interest': total_interest,
        'total_dividend': total_dividend,
        'total_trading': inspector.total_trading(),
        'total_profit': total_profit,
        'total_market_value': total_market_value,
        'total_cash': total_cash
    }
    # avoid negative total_investment when calculating total profit rate
    summary['total_profit_rate'] = summary['total_profit'] / max(summary['total_investment'], 1)
    
    broker = app.config['broker']
    account_info = broker.get_account_info(account)
    return {'summary': summary, 'accountInfo': to_json(account_info)}

@app.route('/account/<account>/positions', methods=['GET'])
def positions(account):
    broker = app.config['broker']
    account_info = broker.get_account_info(account, include_pos=True)
    positions = account_info.positions if account_info else {}
    return jsonify(to_json(positions))

@app.route('/account/<account>/traded_tickers', methods=['GET'])
def traded_tickers(account):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    return {symbol: bool(pos) for symbol, pos in inspector.summarize(False)[2].items()}
    
@app.route('/account/<account>/transaction_groups/<ticker>', methods=['GET'])
def ticker_transaction_groups(account, ticker):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    tx_groups = inspector.ticker_transaction_groups(ticker)
    total, profit, positions, prices = TransactionGroup.summarize(
        tx_groups, True)
    return {
        'transactionGroups': [tx_group.to_json(True) for tx_group in tx_groups],
        'positions': positions,
        'prices': prices,
        'profit': profit,
        'total': total
    }
