import React from 'react';

import { FormattedField } from './format';

import TickerTransactionGroupsPanel from './ticker_transaction_groups_panel';

function SymbolPositionsPanel({ positions, prices }) {
  const symbolPos = { ...prices };
  Object.entries(positions).map(([symbol, qty]) => (
    symbolPos[symbol].push(qty)
  ));
  return (
    <table className="positions">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Quantity</th>
          <th>Price</th>
          <th>Change</th>
          <th>Change(%)</th>
        </tr>
      </thead>
      <tbody>
        {
          Object.entries(symbolPos).map(([symbol, data], index) => (
            <tr key={`symbolPos-${index}`}>
              <td className="symbol">{symbol}</td>
              <td className="quantity">{data[3] || 0}</td>
              <FormattedField value={data[0]} style="currency" />
              <FormattedField value={data[1]} style="currency" />
              <FormattedField value={data[2] / 100} style="percent" />
            </tr>
          ))
        }
      </tbody>
    </table>
  );
}

function TransactionGroupsPanel({ groupInfo, showCompleted }) {
  return (
    <>
      <SymbolPositionsPanel {...groupInfo} />
      <div className="TransactionGroupsPanel">
        {
          groupInfo.groups.map((group, index) => (
            <TickerTransactionGroupsPanel key={`tickerTxGroup-${index}`} {...group} showCompleted={showCompleted} />
          ))
        }
      </div>
    </>
  );
}

export default TransactionGroupsPanel;
