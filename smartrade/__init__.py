# -*- coding: utf-8 -*-

"""smartrade package."""

__author__ = "Hui Zheng"
__copyright__ = "Copyright 2022 Hui Zheng"
__credits__ = ["Hui Zheng"]
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__version__ = "0.3.4"
__maintainer__ = "Hui Zheng"
__email__ = "XYZ.DLL[AT]gmail[DOT]com"
__url__ = "https://github.com/hzheng/smartrade"
__description__ = "a Python application that helps trading decision"

import os
import yaml

from flask import Flask
from flask_assets import Environment, Bundle

from smartrade.BrokerClient import BrokerClient
from smartrade.MarketApi import MarketApi
from smartrade.Logger import Logger

CONF_FILE = os.environ.get('FLASK_CONF_PATH', None)

def create_app(config=None):
    app = Flask(__name__)
    app_name = os.environ.get('FLASK_APP', "smartrade")
    # default configuration
    app.config.from_object(f"{app_name}.settings")
    # user configuration
    if CONF_FILE:
        # app.config.from_envvar(conf_path)
        with open(CONF_FILE, 'r') as cfg_file:
            yaml_conf = yaml.load(cfg_file, yaml.SafeLoader)
            app.config.update(yaml_conf)
    # app specified configuration
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    app.config['version'] = __version__
    return app, Logger(app.config['LOG_FILE'])

app, app_logger = create_app()

def configure_app(config=None):
    if CONF_FILE:
        from smartrade.TDAmeritradeClient import TDAmeritradeClient
        broker = BrokerClient.get_brokers(CONF_FILE)[0]
        app.config['broker'] = broker
        from smartrade.PolygonApi import PolygonApi
        api = MarketApi.get_providers(CONF_FILE)[0]
        from smartrade.MarketDataProvider import MarketDataProvider
        provider = MarketDataProvider(broker, api, app.config['DATABASE'])
        app.config['provider'] = provider
        from smartrade.TransactionGroup import TransactionGroup
        TransactionGroup.set_provider(provider)

configure_app()

def configure_asset():
    assets = Environment(app)
    assets.url = app.static_url_path
    sass = Bundle('sass/style.scss', filters='pyscss', output='generated/all.css')
    assets.register('scss_all', sass)

configure_asset()

from smartrade import jobs

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    jobs.run(app)

import smartrade.views, smartrade.template_utils
import smartrade.rest_api
