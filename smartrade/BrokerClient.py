# -*- coding: utf-8 -*-

from os.path import dirname, join

import yaml

from smartrade.exceptions import ConfigurationError

class BrokerClient:

    def get_account_id(self, account_alias=None): ...
    
    def get_account_info(self, account_alias=None): ...

    def get_transactions(self, account_alias, start_date=None, end_date=None): ...

    def get_quotes(self, symbols): ...
 
    def get_daily_prices(self, symbol, start_date, end_date): ...

    def get_market_hours(self, day): ...

    @classmethod
    def get_brokers(cls, config_path):
        brokers = []
        config_dir = dirname(config_path)
        with open(config_path, 'r') as cfg_file:
            config = yaml.load(cfg_file, yaml.SafeLoader)
            for client in config['broker_client']:
                account_cfg = dict(client, token=join(config_dir, client['token']))
                broker = client['broker'] + "Client"
                for subclass in cls.__subclasses__():
                    if subclass.__name__ == broker:
                        brokers.append(subclass(account_cfg))
                        break
        return brokers