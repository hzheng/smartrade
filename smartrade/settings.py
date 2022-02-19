import os

# default settings

is_dev = (os.getenv('FLASK_ENV') == 'development')

postfix = "-dev" if is_dev else "-prod"

DATABASE = "trading" + postfix
