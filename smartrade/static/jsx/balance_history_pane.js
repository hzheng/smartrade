import React, { useContext, useEffect, useState } from 'react';

import { Button, Divider, Segment, Table } from 'semantic-ui-react';

import AppContext from './app_context';
import { FormattedField } from './format';
import DateRangeSelect from './date_range_select';

import './balance_history_pane.scss';

function BalanceHistoryTable({ data }) {
  return (
    <Table celled fixed className="BalanceHistoryTable">
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Date</Table.HeaderCell>
          <Table.HeaderCell>Balance</Table.HeaderCell>
          <Table.HeaderCell>Actual Balance</Table.HeaderCell>
          <Table.HeaderCell>Difference</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {
          Object.entries(data).map(([date, [bal, actualBal]]) => (
            <Table.Row key={`bal-${date}`}>
              <FormattedField value={date} style="date" />
              <FormattedField value={bal} style="currency" />
              <FormattedField value={actualBal} style="currency" />
              <FormattedField value={actualBal ? (bal - actualBal) / actualBal : null} style="percent" />
            </Table.Row>
          ))
        }
      </Table.Body>
    </Table>
  );
}

function BalanceHistoryPane() {
  const { account, load } = useContext(AppContext);
  const [dateRange, setDateRange] = useState({});
  const [historyData, setHistoryData] = useState({});

  useEffect(() => {
    console.log("Rendering BalancesHistoryPane for account:", account);
    setHistoryData({});
  }, [account]);

  function search() {
    const url = `/account/${account}/balances?dateRange=${dateRange}`;
    load(url, data => { setHistoryData(data); }, "balance history");
  }

  return (
    <Segment className="BalanceHistoryPane">
      <Button icon="find" content="View" onClick={search} />
      <DateRangeSelect onChange={setDateRange} />
      <Divider />
      <BalanceHistoryTable data={historyData} />
    </Segment>
  )
}

export default BalanceHistoryPane;