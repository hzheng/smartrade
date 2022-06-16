from datetime import datetime

from tda import auth, client

from smartrade import app_logger
from smartrade.BrokerClient import BrokerClient
from smartrade.exceptions import ParameterError
from smartrade.utils import http_response

logger = app_logger.get_logger(__name__)

class TDAmeritradeClient(BrokerClient):
    def __init__(self, config):
        token_path = config['token']
        api_key = config['api_key']
        redirect_uri = config['redirect_uri']
        self._accounts = config['accounts']
        try:
            self._client = auth.client_from_token_file(token_path, api_key)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome() as driver:
                self._client = auth.client_from_login_flow(
                    driver, api_key, redirect_uri, token_path)

    def get_account_id(self, account_alias=None):
        for account in self._accounts:
            for key, value in account.items():
                if key == account_alias or value == account_alias or value[-4:] == account_alias:
                    return value

        if not account_alias or isinstance(account_alias, int) or account_alias.isdigit():
            index = int(account_alias) if account_alias else 0
            if index >= len(self._accounts):
                raise ParameterError(f"account index {index} is too large")
            return next(iter(self._accounts[index].values()))
            
        raise ParameterError("cannot find account alias: " + account_alias)

    def get_transactions(self, account_alias=None, start_date=None, end_date=None):
        account_id = self.get_account_id(account_alias)
        if len(account_id) <= 4:
            logger.info("skipping get_transaction for account: %s", account_id)
            return {}

        logger.debug("BEGIN: get_transaction for account %s", account_id)
        # if start_date is not None, unsettled transactions will be ignored
        r = self._client.get_transactions(account_id,
                                          start_date=start_date, end_date=end_date)
        logger.debug("END: get_transaction for account %s", account_id)
        return http_response(r)

    def get_quotes(self, symbols):
        logger.debug("get quotes for %s", symbols)
        r = self._client.get_quotes(symbols)
        return http_response(r)

    def get_daily_prices(self, symbol, start_date, end_date):
        logger.debug("get daily price for %s during %s - %s", symbol, start_date, end_date)
        r = self._client.get_price_history_every_day(
            symbol, start_datetime=start_date, end_datetime=end_date)
        
        res = http_response(r)['candles']
        for obj in res:
            obj['time'] = datetime.fromtimestamp(obj.pop('datetime') / 1000)
        return res

    # TODO: add more arguments
    def get_prices(self, symbol):
        logger.debug("get price for %s", symbol)
        r = self._client.get_price_history(symbol,
                                           period_type=client.Client.PriceHistory.PeriodType.YEAR,
                                           period=client.Client.PriceHistory.Period.TWENTY_YEARS,
                                           frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
                                           frequency=client.Client.PriceHistory.Frequency.DAILY)
        res = http_response(r)['candles']
        for obj in res:
            obj['time'] = datetime.fromtimestamp(obj.pop('datetime') / 1000)
        return res
