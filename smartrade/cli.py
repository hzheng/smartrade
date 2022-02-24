# -*- coding: utf-8 -*-

import sys
import traceback
import yaml
from argparse import ArgumentParser, ArgumentTypeError
from dateutil.parser import parse
from pprint import pprint
from os import listdir
from os.path import expanduser, dirname, abspath, join
import json

from smartrade.Assembler import Assembler
from smartrade.BrokerClient import BrokerClient
from smartrade.exceptions import ConfigurationError
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader
from smartrade.TDAmeritradeClient import TDAmeritradeClient
from smartrade.TransactionGroup import TransactionGroup


def load_db(db_name, path, reload=True):
    loader = Loader(db_name)
    return loader.load(path, reload)

def total_investment(db_name, end_date=None, start_date=None):
    inspector = Inspector(db_name)
    return inspector.total_investment(end_date, start_date)

def total_cash(db_name, end_date=None, start_date=None):
    inspector = Inspector(db_name)
    return inspector.total_cash(end_date, start_date)

def distinct_tickers(db_name, end_date=None, start_date=None):
    inspector = Inspector(db_name)
    return inspector.distinct_tickers(end_date, start_date)

def ticker_costs(db_name, ticker, end_date=None, start_date=None):
    inspector = Inspector(db_name)
    return inspector.ticker_costs(ticker, end_date, start_date)

def ticker_transaction_groups(db_name, ticker):
    inspector = Inspector(db_name)
    return inspector.ticker_transaction_groups(ticker)

def group_transactions(db_name, ticker, save_db=False):
    return Assembler(db_name).group_transactions(ticker, save_db)

def get_broker(config, account_alias):
    cfg_path = expanduser(config['conf_path'])
    return BrokerClient.get_broker(cfg_path, account_alias)


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
    argument('-r', '--reload', action='store_true',
             help="empty database before importing")
)

filter_options = (
    argument('-s', '--start-date', help='start date'),
    argument('-e', '--end-date', help='end date')
)

@subcommand(*data_options, *filter_options,
            argument('-a', '--account', help='account name'),
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"))
def load(config, args):
    """Load transactions."""
    env = _get_env(args)
    db_name = args.database_name or config['DATABASE'][env]
    data_dir = args.data_dir or config['DATA_DIR'][env]
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir) if f.endswith('.csv') or f.endswith('.json')])
    client = get_broker(config, args.account or config['ACCOUNT_ALIAS'])
    TransactionGroup.set_broker(client)
    loader = Loader(db_name)
    loader.load(data_files[0], True)
    for f in data_files[1:]:
        loader.load(f, False)
    assembler = Assembler(db_name)
    inspector = Inspector(db_name)
    for ticker in (args.ticker if args.ticker else inspector.distinct_tickers(args.end_date, args.start_date)):
        ticker = ticker.upper()
        _display_transaction_groups(ticker, assembler.group_transactions(ticker, args.save_database))

@subcommand(*data_options, *filter_options,
            argument('-a', '--account', help='account name'),
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"))
def report(config, args):
    """Report transactions."""
    env = _get_env(args)
    db_name = args.database_name or config['DATABASE'][env]
    inspector = Inspector(db_name)
    client = get_broker(config, args.account or config['ACCOUNT_ALIAS'])
    TransactionGroup.set_broker(client)
    for ticker in (args.ticker if args.ticker else inspector.distinct_tickers(args.end_date, args.start_date)):
        ticker = ticker.upper()
        _display_transaction_groups(ticker, inspector.ticker_transaction_groups(ticker))

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
    argument('-a', '--account', help='account name'),
    argument('symbols', nargs="+", help="symbol"))
def quote(config, args):
    """Quote a symbol(s)."""
    client = get_broker(config, args.account or config['ACCOUNT_ALIAS'])
    pprint(client.get_quotes(args.symbols))

@subcommand(*filter_options,
    argument('-a', '--account', help='account name'))
def transaction(config, args):
    """Get transactions."""
    client = get_broker(config, args.account or config['ACCOUNT_ALIAS'])
    start_date = parse(args.start_date) if args.start_date else None
    end_date = parse(args.end_date) if args.end_date else None
    tx = client.get_transactions(start_date, end_date)
    print(json.dumps(tx, indent=4, sort_keys=True))

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

    cfg_path = join(dirname(abspath(__file__)), "../smartrade.yml")
    with open(cfg_path, 'r') as cfg_file:
        config = yaml.load(cfg_file, yaml.SafeLoader)
    args.function(config, args)


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
