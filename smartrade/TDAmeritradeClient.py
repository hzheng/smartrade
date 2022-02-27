from tda import auth

from smartrade.BrokerClient import BrokerClient
from smartrade.exceptions import ParameterError

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

    def get_accounts(self):
        return self._accounts

    def get_transactions(self, account_alias, start_date=None, end_date=None):
        account_id = None
        if not account_alias or account_alias.isdigit():
            index = int(account_alias) if account_alias else 0
            if index >= len(self._accounts):
                raise ParameterError(f"account index {index} is too large")
            account_id = next(iter(self._accounts[index].values()))
        else:
            for account in self._accounts:
                if account_alias in account:
                    account_id = account[account_alias]
                    break
        if not account_id:
            raise ParameterError("cannot find account alias: " + account_alias)
        r = self._client.get_transactions(account_id,
                                          start_date=start_date, end_date=end_date)
        assert r.status_code == 200, r.raise_for_status()
        return r.json()

    def get_quotes(self, symbols):
        r = self._client.get_quotes(symbols)
        assert r.status_code == 200, r.raise_for_status()
        return {symbol: (prices['bidPrice'] + prices['askPrice']) / 2
                for (symbol, prices) in r.json().items()}
