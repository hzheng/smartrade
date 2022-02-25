# -*- coding: utf-8 -*-

"""smartrade package."""

__author__ = "Hui Zheng"
__copyright__ = "Copyright 2022 Hui Zheng"
__credits__ = ["Hui Zheng"]
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__version__ = "0.1"
__maintainer__ = "Hui Zheng"
__email__ = "XYZ.DLL[AT]gmail[DOT]com"
__url__ = "https://github.com/hzheng/smartrade"
__description__ = "a Python application that helps trading decision"

import os
import yaml

from flask import Flask

from smartrade.BrokerClient import BrokerClient
from smartrade.TDAmeritradeClient import TDAmeritradeClient
from smartrade.TransactionGroup import TransactionGroup

def create_app(config=None):
    app = Flask(__name__)
    app_name = os.environ.get('FLASK_APP', "smartrade")
    # default configuration
    app.config.from_object(f"{app_name}.settings")
    # user configuration
    conf_path = 'FLASK_CONF_PATH'
    if conf_path in os.environ:
        # app.config.from_envvar(conf_path)
        conf_file = os.environ[conf_path]
        client = BrokerClient.get_brokers(conf_file)[0]
        TransactionGroup.set_broker(client)
        with open(conf_file, 'r') as cfg_file:
            yaml_conf = yaml.load(cfg_file, yaml.SafeLoader)
            app.config.update(yaml_conf)
    # app specified configuration
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    return app

app = create_app()

import smartrade.views