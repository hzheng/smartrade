# -*- coding: utf-8 -*-

import json
import sys
import traceback
import yaml
from argparse import ArgumentParser, ArgumentTypeError
from os import listdir
from os.path import expanduser, dirname, abspath, join
from pprint import pprint

from dateutil.parser import parse

from smartrade.Assembler import Assembler
from smartrade.BrokerClient import BrokerClient
from smartrade.exceptions import ConfigurationError
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.MarketDataProvider import MarketDataProvider
from smartrade.TDAmeritradeClient import TDAmeritradeClient
from smartrade.TransactionGroup import TransactionGroup


def load_db(db_name, account, path, reload=True):
    loader = Loader(db_name, account)
    return loader.load(path, reload)

def total_investment(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_investment(start_date, end_date)

def total_interest(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_interest(start_date, end_date)

def total_dividend(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_dividend(start_date, end_date)

def total_trading(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_trading(start_date, end_date)

def total_cash(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_cash(start_date, end_date)

def total_profit(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.total_profit(start_date, end_date)

def distinct_tickers(db_name, account, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.distinct_tickers(start_date, end_date)

def ticker_costs(db_name, account, ticker, start_date=None, end_date=None):
    inspector = Inspector(db_name, account)
    return inspector.ticker_costs(ticker, start_date, end_date)

def ticker_transaction_groups(db_name, account, ticker):
    inspector = Inspector(db_name, account)
    return inspector.ticker_transaction_groups(ticker)

def group_transactions(db_name, account, ticker, save_db=False):
    return Assembler(db_name, account).group_transactions(ticker, save_db)

def get_broker(config):
    cfg_path = expanduser(config['conf_path'])
    return BrokerClient.get_brokers(cfg_path)[0]
    
def get_config():
    cfg_path = join(dirname(abspath(__file__)), "../smartrade.yml")
    with open(cfg_path, 'r') as cfg_file:
        return yaml.load(cfg_file, yaml.SafeLoader)

def get_provider(config, db_name):
    broker = get_broker(config)
    return MarketDataProvider(broker, db_name)

# ============Command Argument Parse============

parser = ArgumentParser(description='Transaction tracking')
subparsers = parser.add_subparsers(dest='subcommand')

def argument(*args, **kwargs):
    return (list(args), kwargs)

def subcommand(*args):
    def decorator(f):
        arg_parser = subparsers.add_parser(f.__name__, description=f.__doc__)
        for arg in args:
            arg_parser.add_argument(*arg[0], **arg[1])
        arg_parser.set_defaults(function=f)

    return decorator


data_options = (
    argument('-E', '--env', help='environment (one of test, dev and prod)'),
    argument('-d', '--data-dir', help='directory of imported data'),
    argument('-D', '--database-name', help='database name'),
    argument('-S', '--save-database', action='store_true', help='save to database'),
    argument('-l', '--live', action='store_true',
             help="live load"),
    argument('-r', '--reload', action='store_true',
             help="empty database before importing")
)

filter_options = (
    argument('-s', '--start-date', help='start date'),
    argument('-e', '--end-date', help='end date')
)

@subcommand(*data_options, *filter_options,
            argument('-v', '--verbose', action='store_true', help='show transaction groups'),
            argument('-a', '--account', help='account id or alias or index'),
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"))
def load(config, args):
    """Load transactions."""
    env = _get_env(args)
    db_name = args.database_name or config['DATABASE'][env]
    broker = get_broker(config)
    account_id = broker.get_account_id(args.account)
    provider = MarketDataProvider(broker, db_name)
    TransactionGroup.set_provider(provider)
    loader = Loader(db_name, account_id, broker)
    start_date = parse(args.start_date) if args.start_date else None
    end_date = parse(args.end_date) if args.end_date else None
    data_dir = args.data_dir or config['DATA_DIR'][env]
    account = account_id[-4:]
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir)
                         if f.startswith(account) and (f.endswith('.csv') or f.endswith('.json'))])
    if args.live:
        transactions = loader.live_load(
            start_date=start_date, end_date=end_date)
        i = 0
        for tx in transactions:
            i += 1
            print(i, "=======", tx)
    else:
        loader.load(data_files[0], args.reload)
        for f in data_files[1:]:
            loader.load(f, False)
    assembler = Assembler(db_name, account_id)
    inspector = Inspector(db_name, account_id)
    for ticker in (args.ticker if args.ticker else inspector.distinct_tickers(args.start_date, args.end_date)):
        ticker = ticker.upper()
        tx_groups = assembler.group_transactions(ticker, args.save_database)
        if args.verbose:
            _display_transaction_groups(ticker, tx_groups)
        else:
            print(f"ticker {ticker} has {len(tx_groups)} group(s)")

@subcommand(*data_options, *filter_options,
            argument('-v', '--verbose', action='store_true', help='show transaction groups'),
            argument('-a', '--account', help='account id or alias or index'),
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"))
def report(config, args):
    """Report transactions."""
    env = _get_env(args)
    db_name = args.database_name or config['DATABASE'][env]
    broker = get_broker(config)
    account_id = broker.get_account_id(args.account)
    inspector = Inspector(db_name, account_id)
    provider = get_provider(config, db_name)
    TransactionGroup.set_provider(provider)
    for ticker in (args.ticker if args.ticker else inspector.distinct_tickers(args.start_date, args.end_date)):
        ticker = ticker.upper()
        tx_groups = inspector.ticker_transaction_groups(ticker)
        if args.verbose:
            _display_transaction_groups(ticker, tx_groups)
        else:
            print(f"ticker {ticker} has {len(tx_groups)} group(s)")

def _display_transaction_groups(ticker, tx_groups):
    print("=========ticker:", ticker)
    i = 0
    for group in tx_groups:
        i += 1
        print(f"-----group {i}------")
        print(f"profit: {group.profit}")
        for leading, following in group.chains.items():
            print(leading, "=>")
            for tx in following:
                print("\t", tx.date, "qty:", tx.quantity, "price:", tx.price, "amount:", tx.amount)

@subcommand(
    *data_options,
    argument('-t', '--date', help='date'),
    argument('-a', '--account', help='account id or alias or index'),
    argument('symbols', nargs="+", help="symbol"))
def quote(config, args):
    """Quote a symbol(s)."""
    env = _get_env(args)
    db_name = args.database_name or config['DATABASE'][env]
    provider = get_provider(config, db_name)
    pprint(provider.get_quotes(args.symbols, args.date))


@subcommand(*filter_options,
    argument('-a', '--account', help='account id or alias or index'))
def transaction(config, args):
    """Get transactions."""
    client = get_broker(config)
    start_date = parse(args.start_date) if args.start_date else None
    end_date = parse(args.end_date) if args.end_date else None
    tx = client.get_transactions(args.account, start_date, end_date)
    print(json.dumps(tx, indent=4, sort_keys=False))

def _get_env(args):
    env = args.env or 'test'
    if env not in ('test', 'dev', 'prod'):
        raise ValueError("env must be one of test, dev and prod")
    return env

def main():
    # read command args
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        return

    args.function(get_config(), args)


if __name__ == '__main__':
    exit_code = 1
    try:
        main()
        exit_code = 0
    except (ConfigurationError, yaml.YAMLError) as ce:
        print("Please fix the configuration setting:", ce)
    except OSError as oe:
        print("Please fix the OS-related problem:", oe)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print("Please report the bug:", e)
    finally:
        sys.exit(exit_code)
