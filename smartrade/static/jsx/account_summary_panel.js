import React, { useContext, useEffect, useState } from 'react';

import { FormattedNumber } from 'react-intl';

import AppContext from "./app_context";
import { fetchData } from "./util";

function AccountSummaryPanel() {
  const { account } = useContext(AppContext);
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
    setSummary(accountSummary);
  }

  useEffect(() => {
    (async () => {
      const res = await fetchData(`/account/${account}/summary`);
      const data = await res.json();
      loadAccountSummary(data);
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
            <td className="money amount"><FormattedNumber value={summary.account_value} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.profit} style="currency" currency="USD" /></td>
            <td className="amount"><FormattedNumber value={summary.profit_rate} style='percent' minimumFractionDigits={2} /></td>
            <td className="money amount"><FormattedNumber value={summary.total_securities_value} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.cash_value} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.margin_balance} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.total_investment} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.total_interest} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.total_dividend} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.buying_power} style="currency" currency="USD" /></td>
            <td className="money amount"><FormattedNumber value={summary.nonmarginable_buying_power} style="currency" currency="USD" /></td>
          </tr>
        </tbody>
      </table>
    </div >
  )
}

export default AccountSummaryPanel;
