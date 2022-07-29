import React from 'react';

import { Table } from 'semantic-ui-react';

import { FormattedField } from './format';

function TransactionGroupsSummaryPanel({ summary, total }) {
  return (
    total &&
    <Table className="TransactionGroupsSummaryPanel">
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Ticker</Table.HeaderCell>
          <Table.HeaderCell>Market Value</Table.HeaderCell>
          <Table.HeaderCell>Profit</Table.HeaderCell>
          <Table.HeaderCell>Investment</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {
          Object.entries(summary).map(([ticker, [investment, profit]], index) => (
            <Table.Row key={`txGroupsSummary-${index}`}>
              <Table.Cell>{ticker}</Table.Cell>
              <FormattedField value={investment + profit} style="currency" />
              <FormattedField value={profit} style="currency" />
              <FormattedField value={investment} style="currency" />
            </Table.Row>
          ))
        }
      </Table.Body>
      {
        (Object.entries(summary).length > 1) &&
        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell>Total</Table.HeaderCell>
            <FormattedField value={total[0] + total[1]} style="currency" tag="th" />
            <FormattedField value={total[1]} style="currency" tag="th" />
            <FormattedField value={total[0]} style="currency" tag="th" />
          </Table.Row>
        </Table.Footer>
      }
    </Table>
  );
}

export default TransactionGroupsSummaryPanel;
