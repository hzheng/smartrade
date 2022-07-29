import React, { useContext, useEffect, useState } from 'react';

import { Button, Divider, Segment, Table } from 'semantic-ui-react';

import AppContext from './app_context';
import { FormattedField } from './format';
import FileSelect from './file_select';
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

  function uploadFile(fileOptions) {
    console.log("uploading file ", fileOptions);
    const url = `/account/${account}/balances`;
    load(url, data => { console.log("response=",data); }, "balance history", fileOptions);
  }

  function validateFile(file) {
    const fileName = file.name;
    if (fileName.indexOf(account) < 0) {
      return `file name ${fileName} should contains account#: ${account}`;
    }
  }

  function search() {
    const arg = (dateRange == "" || dateRange == null) ? "" : `dateRange=${dateRange}`;
    const url = `/account/${account}/balances?${arg}`;
    load(url, data => { setHistoryData(data); }, "balance history");
  }

  return (
    <Segment className="BalanceHistoryPane">
      <FileSelect title="Upload balance history file" icon="upload" validate={validateFile} onSubmit={uploadFile} />
      <Button icon="find" content="View" onClick={search} />
      <DateRangeSelect onChange={setDateRange} />
      <Divider />
      <BalanceHistoryTable data={historyData} />
    </Segment>
  )
}

export default BalanceHistoryPane;