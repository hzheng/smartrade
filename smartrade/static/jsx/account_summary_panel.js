import React, { useContext, useEffect, useState } from 'react';

import { FormattedField } from './format';

import AppContext from "./app_context";

function AccountSummaryPanel() {
  const { account, load } = useContext(AppContext);
  const [summary, setSummary] = useState({});

  function loadAccountSummary(data) {
    const accountInfo = data.accountInfo;
    const balance = accountInfo && accountInfo.balance;
    let accountSummary = {};
    if (balance) {
      accountSummary = { ...balance };
      let marketValue = balance.account_value;
      const cost = data.summary.total_investment;
      const profit = marketValue - cost;
      accountSummary['profit'] = profit;
      accountSummary['profit_rate'] = profit / cost;
    }
    for (const [key, value] of Object.entries(data.summary)) { // may override the above values
      accountSummary[key] = value;
    }
    if (!balance) {
      accountSummary['account_value'] = accountSummary['total_market_value'];
      accountSummary['cash_value'] = accountSummary['total_cash'];
      accountSummary['profit'] = accountSummary['total_profit'];
      accountSummary['profit_rate'] = accountSummary['total_profit_rate'];
    }
    setSummary(accountSummary);
  }

  useEffect(() => {
    load(`/account/${account}/summary`,
      data => { loadAccountSummary(data); }, "account summary");
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
            <FormattedField value={summary.account_value} style="currency" />
            <FormattedField value={summary.profit} style="currency" />
            <FormattedField value={summary.profit_rate} style="percent" />
            <FormattedField value={summary.total_securities_value} style="currency" />
            <FormattedField value={summary.cash_value} style="currency" />
            <FormattedField value={summary.margin_balance} style="currency" />
            <FormattedField value={summary.total_investment} style="currency" />
            <FormattedField value={summary.total_interest} style="currency" />
            <FormattedField value={summary.total_dividend} style="currency" />
            <FormattedField value={summary.buying_power} style="currency" />
            <FormattedField value={summary.nonmarginable_buying_power} style="currency" />
          </tr>
        </tbody>
      </table>
    </div >
  )
}

export default AccountSummaryPanel;
