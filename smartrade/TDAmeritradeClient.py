from tda import auth

from smartrade.BrokerClient import BrokerClient


class TDAmeritradeClient(BrokerClient):
    def __init__(self, config):
        token_path = config['token_path']
        api_key = config['api_key']
        redirect_uri = config['redirect_uri']
        self._account_no = config['account_no']
        try:
            self._client = auth.client_from_token_file(token_path, api_key)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome() as driver:
                self._client = auth.client_from_login_flow(
                    driver, api_key, redirect_uri, token_path)

    def get_transactions(self):
        r = self._client.get_transactions(self._account_no)
        assert r.status_code == 200, r.raise_for_status()
        return r.json()

    def get_quotes(self, symbols):
        r = self._client.get_quotes(symbols)
        assert r.status_code == 200, r.raise_for_status()
        return {symbol : prices['lastPrice'] for (symbol, prices) in r.json().items()}