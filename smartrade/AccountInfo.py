# -*- coding: utf-8 -*-

from smartrade.utils import check

class BalanceInfo:
    def __init__(self, **vals):
        for key, val in vals.items():
            setattr(self, "_" + key, val)
        check(abs(self.account_value - self.cash_value - self.total_securities_value - self.margin_balance) < 1e-9,
              f"{self.account_value} should be almost equal to {self.cash_value} + {self.total_securities_value} + {self.margin_balance}")

    @property
    def account_value(self):
        """Account value (i.e. total equity)."""
        return self._account_value

    @property
    def cash_value(self):
        """Cash value (i.e. total cash)."""
        return self._cash_value

    @property
    def buying_power(self):
        """Buying power (i.e. purchasing power)."""
        return self._buying_power

    @property
    def long_stock_value(self):
        return self._long_stock_value

    @property
    def short_stock_value(self):
        return self._short_stock_value

    @property
    def long_stock_value(self):
        return self._long_stock_value

    @property
    def long_option_value(self):
        return self._long_option_value

    @property
    def short_option_value(self):
        return self._short_option_value

    @property
    def stock_value(self):
        return self.long_stock_value + self.short_stock_value

    @property
    def option_value(self):
        return self.long_option_value + self.short_option_value

    @property
    def long_value(self):
        return self.long_stock_value + self.long_option_value

    @property
    def short_value(self):
        return self.short_stock_value + self.short_option_value

    @property
    def total_securities_value(self):
        return self.long_value + self.short_value

    @property
    def total_interest(self):
        return self._total_interest

    @property
    def margin_balance(self):
        return self._margin_balance

    @property
    def margin_equity(self):
        return self._margin_equity

    @property
    def maint_req(self):
        """The minimum amount of equity needed to hold marginable positions."""
        return self._maint_req

    def __repr__(self):
        return (f"account_value={self.account_value}, cash_value={self.cash_value:.2f}, total_interest={self.total_interest}, "
                f"margin_balance={self.margin_balance}, margin_equity={self.margin_equity}, "
                f"maint_req={self.maint_req}, total_securities_value={self.total_securities_value:.2f}, "
                f"long_stock_value={self.long_stock_value}, short_stock_value={self.short_stock_value}, "
                f"long_option_value={self.long_option_value}, short_option_value={self.short_option_value}")

class PositionInfo:
    def __init__(self, **vals):
        for key, val in vals.items():
            setattr(self, "_" + key, val)

    @property
    def symbol(self):
        return self._symbol

    @property
    def quantity(self):
        return self._quantity

    @property
    def quantity(self):
        return self._quantity

    @property
    def price(self):
        return self._price

    @property
    def cost(self):
        return self._cost

    @property
    def day_gain(self):
        return self._day_gain

    @property
    def day_gain_percent(self):
        return self._day_gain_percent

    @property
    def day_cost(self):
        return self._day_cost

    @property
    def pre_quantity(self):
        return self._pre_quantity

    @property
    def maint_req(self):
        return self._maint_req

    def __repr__(self):
        return (f"symbol={self.symbol}, quantity={self.quantity}, price={self.price:.2f}, "
                f"cost={self.cost}, day_gain={self.day_gain:.2f}, day_gain_percent={self.day_gain_percent}, "
                f"day_cost={self.day_cost}, pre_quantity={self.pre_quantity}, maint_req={self.maint_req}")

class LegInfo:
    def __init__(self, **vals):
        for key, val in vals.items():
            setattr(self, "_" + key, val)

    @property
    def symbol(self):
        return self._symbol

    @property
    def quantity(self):
        return self._quantity

    @property
    def action(self):
        return self._action

    def __repr__(self):
        return f"symbol={self.symbol}, quantity={self.quantity}, action={self.action}"

class OrderInfo:
    def __init__(self, **vals):
        for key, val in vals.items():
            setattr(self, "_" + key, val)

    @property
    def legs(self):
        return self._legs

    @property
    def order_type(self):
        return self._order_type

    @property
    def status(self):
        return self._status

    @property
    def price(self):
        return self._price

    @property
    def quantity(self):
        return self._quantity

    @property
    def filled_quantity(self):
        return self._filled_quantity

    @property
    def strategy_type(self):
        return self._strategy_type

    @property
    def duration(self):
        return self._duration

    @property
    def cancel_time(self):
        return self._cancel_time

    def __repr__(self):
        return (f"legs={{{self.legs}}}, price={self.price}, quantity={self.quantity}, "
                f"filled_quantity={self.filled_quantity}, order_type={self.order_type}, "
                f"status={self.status}, strategy_type={self.strategy_type}, "
                f"duration={self.duration}, cancel_time={self.cancel_time}")

class AccountInfo:
    def __init__(self, acct_id, cur_bal, pre_bal, **vals):
        self._account_id = acct_id
        self._cur_bal = cur_bal
        self._pre_bal = pre_bal
        for key, val in vals.items():
            setattr(self, "_" + key, val)

    @property
    def account_id(self):
        return self._account_id

    @property
    def balance(self):
        return self._cur_bal

    @property
    def pre_balance(self):
        return self._pre_bal

    @property
    def positions(self):
        return self._positions

    @property
    def orders(self):
        return self._orders

    @property
    def account_type(self):
        return self._account_type

    @property
    def day_trader(self):
        return self._day_trader

    def __repr__(self):
        return (f"account={self.account_id}, balance={{{self.balance}}}, pre_balance={{{self.pre_balance}}}, "
                f"positions={{{self.positions}}}, orders={{{self.orders}}}, "
                f"account_type={self.account_type}, day_trader={self.day_trader}")
