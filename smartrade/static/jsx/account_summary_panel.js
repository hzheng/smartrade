import React, { useContext, useEffect } from 'react';

import $ from 'jquery';

import AppContext from "./app_context";
import { fetchData, resetValues, setValue } from "./util";

function AccountSummaryPanel() {
  const { account } = useContext(AppContext);

  function loadAccountSummary(data, $self) {
    const accountInfo = data.accountInfo;
    const balance = accountInfo && accountInfo.balance;
    if (balance) {
      for (const [key, value] of Object.entries(balance)) {
        setValue($('td[name="' + key + '"]', $self), value);
      }
      let marketValue = balance.account_value;
      const cost = data.summary.total_investment;
      const profit = marketValue - cost;
      setValue($('td[name="profit"]', $self), profit);
      setValue($('td[name="profit_rate"]', $self), profit / cost);
    }
    for (const [key, value] of Object.entries(data.summary)) { // may override the above values
      setValue($('td[name="' + key + '"]', $self), value);
    }
  }

  useEffect(() => {
    const $self = $(".AccountSummaryPanel");
    resetValues($self, "???");
    (async () => {
      const res = await fetchData(`/account/${account}/summary`);
      const data = await res.json();
      loadAccountSummary(data, $self);
    })();
  }, [account]);

  return (
    <div className="AccountSummaryPanel">
      <table>
        <tbody>
          <tr>
            <th>Total</th>
            <th>Profit</th>
            <th>Profit(%)</th>
            <th>Securities</th>
            <th>Cash</th>
            <th>Margin</th>
            <th>Investment</th>
            <th>Interest</th>
            <th>Dividend</th>
            <th>Stock Buying Power</th>
            <th>Option Buying Power</th>
          </tr>
          <tr>
            <td className="money amount" name="account_value"></td>
            <td className="money amount" name="profit"></td>
            <td className="amount percent" name="profit_rate"></td>
            <td className="money amount" name="total_securities_value"></td>
            <td className="money amount" name="cash_value"></td>
            <td className="money amount" name="margin_balance"></td>
            <td className="money amount" name="total_investment"></td>
            <td className="money amount" name="total_interest"></td>
            <td className="money amount" name="total_dividend"></td>
            <td className="money amount" name="buying_power"></td>
            <td className="money amount" name="nonmarginable_buying_power"></td>
          </tr>
        </tbody>
      </table>
    </div >
  )
}

export default AccountSummaryPanel;
