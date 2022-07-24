import React from 'react';

import { FormattedField } from './format';

function TransactionGroupsSummaryPanel({ summary, total }) {
  return (
    total &&
    <table className="TransactionGroupsSummaryPanel">
      <thead>
        <tr><th>Ticker</th><th>Market Value</th><th>Profit</th><th>Investment</th></tr>
      </thead>
      <tbody>
        {
          Object.entries(summary).map(([ticker, [investment, profit]], index) => (
            <tr key={`txGroupsSummary-${index}`}>
              <td>{ticker}</td>
              <FormattedField value={investment + profit} style="currency" />
              <FormattedField value={profit} style="currency" />
              <FormattedField value={investment} style="currency" />
            </tr>
          ))
        }
        <tr>
          <td>Total</td>
          <FormattedField value={total[0] + total[1]} style="currency" />
          <FormattedField value={total[1]} style="currency" />
          <FormattedField value={total[0]} style="currency" />
        </tr>
      </tbody>
    </table>
  );
}

export default TransactionGroupsSummaryPanel;
