# -*- coding: utf-8 -*-

from smartrade.Assembler import Assembler
from smartrade.Inspector import Inspector
from smartrade.Loader import Loader

from datetime import datetime
from pprint import pprint
import sys
import traceback
from argparse import ArgumentParser, ArgumentTypeError
import yaml
from os import listdir
from os.path import join

DEFAULT_DB_NAME = "trading_test"

def load_db(db_name, path, reload=True):
    loader = Loader(db_name)
    return loader.load(path, reload)

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
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"),
            argument('-C', '--csv', action='store_true',
                     help="in CSV format"))
def load(args):
    """Report transactions."""
    db_name = args.database_name or DEFAULT_DB_NAME
    data_dir = args.data_dir or "smartrade/test"
    data_files = sorted([join(data_dir, f) for f in listdir(data_dir) if f.endswith('.csv')])
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
            argument('-t', '--ticker', nargs='+', help="ticker name(s)"),
            argument('-C', '--csv', action='store_true',
                     help="in CSV format"))
def report(args):
    """Report transactions."""
    db_name = args.database_name or DEFAULT_DB_NAME
    inspector = Inspector(db_name)
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

def main():
    # read command args
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        return

    args.function(args)


if __name__ == '__main__':
    exit_code = 1
    try:
        main()
        exit_code = 0
    except OSError as oe:
        print("Please fix the OS-related problem:", oe)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print("Please report the bug:", e)
    finally:
        sys.exit(exit_code)
