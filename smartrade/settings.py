import os

# default settings for Flask app

env = os.getenv('FLASK_ENV')

if not env:
    postfix = "_test"
else:
    postfix = "_prod" if env == 'production' else "_dev"

DATABASE = "trading" + postfix

DATA_DIR = os.getenv('TRADE_DATA')

LOG_FILE = f"/var/log/smartrade/smartrade{postfix}.log"
