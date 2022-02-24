# -*- coding: utf-8 -*-

from os.path import dirname, join

import yaml

from smartrade.exceptions import ConfigurationError

class BrokerClient:

    def get_transactions(self, start_date=None, end_date=None): ...

    def get_quotes(self, symbols): ...

    @classmethod
    def get_broker(cls, config_path, account_alias):
        config_dir = dirname(config_path)
        with open(config_path, 'r') as cfg_file:
            config = yaml.load(cfg_file, yaml.SafeLoader)
            account_cfg = config['accounts'][account_alias]
            account_cfg['token_path'] = join(config_dir, account_alias + "_token.json")
            broker = account_cfg['broker'] + "Client"
            for subclass in cls.__subclasses__():
                if subclass.__name__ == broker:
                    return subclass(account_cfg)
            raise ConfigurationError(f"no broker named {broker} found")