# -*- coding: utf-8 -*-

import re

from dateutil.parser import parse
from flask import jsonify, render_template, request, session

from smartrade import app, app_logger
from smartrade.Assembler import Assembler
from smartrade.exceptions import TooManyRequestsError 
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TransactionGroup import TransactionGroup
from smartrade.utils import CustomJsonEncoder, parse_date_range, to_json

logger = app_logger.get_logger(__name__)

app.json_encoder = CustomJsonEncoder


@app.route("/")
def index():
    accounts = app.config['broker_client'][0]['accounts']
    default_account = list(accounts[0].values())[0][-4:]  # TODO: get from login
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
    position_map = {symbol: qty for pos_map in positions.values()
                    for symbol, qty in pos_map.items()}
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


@app.route('/account/<account>/transaction_groups/<tickers>', methods=['GET'])
def ticker_transaction_groups(account, tickers):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)
    res = {}
    for ticker in tickers.split(","):
        tx_groups = inspector.ticker_transaction_groups(ticker)
        total, profit, positions, prices = TransactionGroup.summarize(
            tx_groups, True)
        if ticker in positions:
            res[ticker] = {
                'groups': [tx_group.to_json(True) for tx_group in tx_groups],
                'positions': positions[ticker],
                'prices': prices,
                'profit': profit,
                'investment': -total
            }
    return res


def _get_date_range(context):
    start_date = end_date = None
    date_range = request.args.get('dateRange', ",")
    if "," in date_range:
        start, end = date_range.split(",")
        if start:
            start_date = parse(start)
        if end:
            end_date = parse(end)
    else:
        start_date, end_date = parse_date_range(date_range)
    logger.debug("%s: start_date=%s, end_date=%s",
                 context, start_date, end_date)
    return start_date, end_date


@app.route("/account/<account>/transactions/<tickers>", methods=['GET'])
def ticker_transaction_history(account, tickers):
    db_name = app.config['DATABASE']
    inspector = Inspector(db_name, account)

    start_date, end_date = _get_date_range("transaction_history")
    order = request.args.get('dateOrder') or "1"
    valid = int(request.args.get('valid', "-2"))
    completed = int(request.args.get('completed', "-2"))
    effective = int(request.args.get('effective', "-1"))
    original = int(request.args.get('original', "-1"))
    action = request.args.get('action')
    transactions = inspector.transaction_list(start_date, end_date,
                                              None if tickers == 'all' else tickers,
                                              order == "1", valid, completed, effective, original, action)
    return jsonify([tx.to_json(serialize=True) for tx in transactions])


@app.route('/account/<account>/balances', methods=['GET'])
def balances(account):
    db_name = app.config['DATABASE']
    provider = app.config['provider']
    inspector = Inspector(db_name, account, provider)
    start_date, end_date = _get_date_range("balance_history")
    return inspector.balance_history(start_date, end_date)


@app.route('/account/<account>/balances', methods=['POST'])
def upload_balance_history(account):
    db_name = app.config['DATABASE']
    provider = app.config['provider']
    inspector = Inspector(db_name, account, provider)
    upload_file = request.files.get('file')
    logger.debug("uploading file: %s", upload_file)
    if account not in upload_file.filename:
        return f"uploaded file name should contain account#: {account}", 406

    balance_map = {}
    bal_pattern = re.compile('.*"([^"]+)","([^"]+)"')
    for row in upload_file:
        line = row.decode("utf-8").strip()
        date_str, balance_str = bal_pattern.match(line).groups()
        balance = float(balance_str.replace(',',''))
        logger.debug("date %s %s", date_str, balance)
        balance_map[date_str] = balance
    inspector.save_actual_balance(balance_map)
    return {"uploaded": len(balance_map)}


@app.errorhandler(404)
def page_not_found(err):
    return f"Page not found: {err}", 404

@app.errorhandler(Exception)
def server_error(err):
    logger.exception(err)
    if isinstance(err, TooManyRequestsError):
        return f"Too many requests: {err}", 429

    return f"Exception happened: {err}", 500

