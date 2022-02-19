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
from flask import Flask

def create_app(config=None):
    app = Flask(__name__)
    app_name = os.environ.get('FLASK_APP', "smartrade")
    # default configuration
    app.config.from_object(f"{app_name}.settings")
    # environment configuration
    conf_path_env = 'FLASK_CONF_PATH'
    if conf_path_env in os.environ:
        app.config.from_envvar(conf_path_env)
    # app specified configuration
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    return app

app = create_app()

import smartrade.views