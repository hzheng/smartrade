from datetime import datetime
import time

import requests

from smartrade import app_logger
from smartrade.exceptions import TooManyRequestsError
from smartrade.MarketApi import MarketApi
from smartrade.Transaction import Symbol
from smartrade.utils import http_response

logger = app_logger.get_logger(__name__)

class PolygonApi(MarketApi):
    def __init__(self, config):
        self._api_key = config['api_key']
        self._url = config['url']

    def get_daily_prices(self, symbol, start_date, end_date):
        logger.debug("get daily price for %s", symbol)
        start = start_date.strftime("%Y-%m-%d")
        end = end_date.strftime("%Y-%m-%d")
        symbol_obj = Symbol(symbol)
        s = "O:" + symbol_obj.to_str2() if symbol_obj.is_option() else symbol
        while True:
            try:
                r = requests.get(f"{self._url}/v2/aggs/ticker/{s}/range/1/day/{start}/{end}?apiKey={self._api_key}")
                json = http_response(r)
                count = json.get('resultsCount', -1)
                if count == 0: return []
                if count > 0: break
            except TooManyRequestsError: 
                logger.warning("wait 30 seconds for the next request of the price of symbol %s", symbol)
                time.sleep(30)

        res = r.json()['results']
        for obj in res:
            obj['open'] = obj.pop('o')
            obj['close'] = obj.pop('c')
            obj['high'] = obj.pop('h')
            obj['low'] = obj.pop('l')
            obj['volume'] = obj.pop('v')
            obj['weighted_average'] = obj.pop('vw')
            obj['transactions'] = obj.pop('n')
            obj['time'] = datetime.fromtimestamp(obj.pop('t') / 1000)
        return res