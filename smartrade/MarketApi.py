# -*- coding: utf-8 -*-

import yaml

class MarketApi:

    def get_url(self): ...

    def get_daily_prices(self, symbol, start_date, end_date): ...

    @classmethod
    def get_providers(cls, config_path):
        providers = []
        with open(config_path, 'r') as cfg_file:
            config = yaml.load(cfg_file, yaml.SafeLoader)
            for api in config['market_api']:
                provider = api['provider'] + "Api"
                for subclass in cls.__subclasses__():
                    if subclass.__name__ == provider:
                        providers.append(subclass(api))
                        break
        return providers