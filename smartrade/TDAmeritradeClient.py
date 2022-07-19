# -*- coding: utf-8 -*-

from datetime import datetime

from tda import auth, client
from tda.client.base import BaseClient

from smartrade import app_logger
from smartrade.AccountInfo import AccountInfo, BalanceInfo, LegInfo, OrderInfo, PositionInfo
from smartrade.BrokerClient import BrokerClient
from smartrade.exceptions import BadRequestError, ParameterError
from smartrade.Transaction import Action, Symbol
from smartrade.utils import get_value, http_response

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

    def get_account_info(self, account_alias=None, include_pos=False, include_order=False):
        account_id = self.get_account_id(account_alias)
        if len(account_id) <= 4:
            logger.info("skipping get_account for account: %s", account_id)
            return None

        logger.debug("BEGIN: get_account for account %s", account_id)
        fields = []
        if include_pos:
            fields.append(BaseClient.Account.Fields.POSITIONS)
        if include_order:
            fields.append(BaseClient.Account.Fields.ORDERS)
        r = self._client.get_account(account_id, fields=fields)
        json = http_response(r)
        logger.debug("response: %s", json)
        res = json.get('securitiesAccount', None)
        if not res:
            logger.warn("no account information found")
            return None
        
        cur_bal = self._get_balance(res['currentBalances'])
        pre_bal = self._get_balance(res['initialBalances'])
        positions = self._get_positions(res['positions']) if include_pos else None
        orders = self._get_orders(res.get('orderStrategies', None)) if include_order else None
        return AccountInfo(res['accountId'], cur_bal, pre_bal, 
                           positions=positions, orders=orders,
                           account_type=res['type'],
                           day_trader=res['isDayTrader'])
 
    @classmethod
    def _get_balance(cls, bal):
        return BalanceInfo(
            account_value=bal['liquidationValue'],
            cash_value=bal['cashBalance'] + bal['moneyMarketFund'],  # + bal['accruedInterest'],
            buying_power=get_value(bal, 'buyingPower', 'cashAvailableForTrading', 'availableFundsNonMarginableTrade'),
            nonmarginable_buying_power=get_value(bal, 'availableFundsNonMarginableTrade', 'buyingPower', 'cashAvailableForTrading'),
            long_margin_value=get_value(bal, 'longMarginValue'),
            long_stock_value=get_value(bal, 'longStockValue', 'longMarketValue'),
            short_stock_value=get_value(bal, 'shortStockValue', 'shortMarketValue'),
            long_option_value=bal['longOptionMarketValue'],
            short_option_value=bal['shortOptionMarketValue'],
            total_interest=bal['accruedInterest'],
            margin_equity=get_value(bal, 'equity'),
            maint_req=get_value(bal, 'maintenanceRequirement'),
            margin_balance=get_value(bal, 'marginBalance')
        )

    @classmethod
    def _get_positions(cls, positions):
        res = []
        for p in (positions or []):
            instrument = p['instrument']
            if instrument["assetType"] == "CASH_EQUIVALENT": continue

            qty = p['longQuantity']
            if qty == 0.0:
                qty = -p['shortQuantity']
            pre_qty = p.get('previousSessionLongQuantity', 0.0)
            if pre_qty == 0.0:
                pre_qty = -p.get('previousSessionShortQuantity', 0.0)
            pos = PositionInfo(
                symbol=Symbol(instrument['symbol']),
                quantity=qty,
                price=p['marketValue'] / qty,
                cost=p['averagePrice'],
                day_gain=p['currentDayProfitLoss'],
                day_gain_percent=p['currentDayProfitLossPercentage'],
                day_cost=p['currentDayCost'],
                pre_quantity=pre_qty,
                maint_req=p['maintenanceRequirement']
            )
            res.append(pos)
        return res
 
    @classmethod
    def _get_orders(cls, orders):
        res = []
        for o in orders or []:
            order = OrderInfo(
                legs=cls._get_order(o['orderLegCollection']),
                price=o['price'],
                quantity=o['quantity'],
                filled_quantity=o['filledQuantity'],
                order_type=o['orderType'],
                status=o['status'],
                strategy_type=o['orderStrategyType'],
                duration=o['duration'],
                cancel_time=o.get('cancelTime', None)
            )
            res.append(order)
        return res
    
    @classmethod
    def _get_order(cls, legs):
        res = []
        for leg in legs:
            res.append(LegInfo(
                symbol=Symbol(leg['instrument']['symbol']),
                quantity=leg['quantity'],
                action=Action.from_str(leg['instruction']),
            ))
        return res

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

    def get_market_hours(self, day):
        logger.debug("get hours on the day: %s", day)
        market = client.Client.Markets.EQUITY
        try:
            r = self._client.get_hours_for_multiple_markets([market], day)
            response = http_response(r)
            logger.debug("response: %s", response)
            market_str = str(market).split(".")[-1]
            for v in response[market_str.lower()].values():
                if v.get('marketType', None) == market_str:
                    hours = v['sessionHours']
                    if not hours: return None

                    market_hours = hours['regularMarket'][0]
                    logger.debug("regular market hours: %s", market_hours)
                    start = market_hours['start']
                    end = market_hours['end']
                    return (start, end)
        except BadRequestError:
            logger.warn("bad request")
        return None
