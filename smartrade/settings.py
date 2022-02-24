import os

# default settings for Flask app

is_dev = (os.getenv('FLASK_ENV') == 'development')

postfix = "_dev" if is_dev else "_prod"

DATABASE = "trading" + postfix

DATA_DIR = "smartrade/test" if is_dev else os.getenv('TRADE_DATA')

ACCOUNT_ALIAS = "account0"