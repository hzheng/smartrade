import React, { useContext, useEffect, useState } from 'react';

import { Button, Divider, Message, Segment } from 'semantic-ui-react';

import AppContext from "./app_context";
import DateRangeSelect from './date_range_select';
import FilterSelect from './filter_select';
import TickersSelect from './tickers_select';
import TransactionHistoryTable from './transaction_history_table';

import './transaction_history_pane.scss';

function TransactionFilterPanel({ filters, onCommand }) {
  function update(name, value) {
    filters[name] = value;
  }

  return <div className="TransactionFilterPanel">
    <div>
      <Button icon="find" content="View" onClick={() => onCommand(filters)} />
      <DateRangeSelect onChange={(range) => update('dateRange', range)} />
    </div>
    <div>
      <TickersSelect onChange={(t) => update('tickers', t)} />
    </div>
    <div>
      <FilterSelect title="validity" name="valid" options={{ valid: 1, ignored: 0, invalid: -1 }} defaultValue={1} onChange={update} />
      <FilterSelect title="completion" name="completed" options={{ completed: 1, uncompleted: 0, ungrouped: -1 }} onChange={update} />
      <FilterSelect title="effectivity" name="effective" options={{ effective: 1, ineffective: 0 }} onChange={update} />
      <FilterSelect title="source" name="original" options={{ original: 1, virtual: 0 }} onChange={update} />
      <FilterSelect title="action" name="action" options={{
        open: "BTO,STO",
        close: "STC,BTC,EXPIRED,ASSIGNED,EXERCISE",
        'buy to open': "BTO",
        'sell to open': "STO",
        'sell to close': "STC",
        'buy to close': "BTC",
        expired: "EXPIRED",
        split: "SPLIT,SPLIT_FROM,SPLIT_TO",
        assigned: "ASSIGNED",
        exercise: "EXERCISE",
        transfer: "TRANSFER",
        interest: "INTEREST",
        dividend: "DIVIDEND",
        journal: "JOURNAL"
      }} onChange={update} />
    </div>
  </div>;
}

function TransactionSummaryPanel() {
  return (
    <Message className="TransactionSummaryPanel">
      <div className="legend">
        <span className="note">Note:</span>
        <span className="effective">effective</span>
        <span className="ineffective">ineffective</span>
        <span className="original">original</span>
        <span className="virtual">virtual</span>
        <span className="completed">completed</span>
        <span className="uncompleted">uncompleted</span>
        <span className="merged">merged</span>
        <span className="sliced">sliced</span>
      </div>
    </Message>
  );
}

function TransactionHistoryPane() {
  const { account, load } = useContext(AppContext);

  const [filters, setFilters] = useState({});
  const [historyData, setHistoryData] = useState([]);

  function search(values) {
    setFilters(values);
    const { tickers, ...options } = values;
    const tickerList = tickers && tickers.length ? tickers.join(",") : "all";
    const params = Object.entries(options).map(([key, val]) => (val === "" || val == null) ? "" : `${key}=${val}`);
    const url = `/account/${account}/transactions/${tickerList}?${params.join('&')}`;
    load(url, data => { setHistoryData(data); }, `transaction history(${tickerList})`);
  }

  useEffect(() => {
    console.log("Rendering TransactionHistoryPane for account:", account);
    setHistoryData([]);
  }, [account, filters]);

  return (
    <Segment className="TransactionHistoryPane">
      <TransactionFilterPanel filters={filters} onCommand={search} />
      <TransactionSummaryPanel />
      <Divider />
      <TransactionHistoryTable historyData={historyData} />
    </Segment>
  )
}

export default TransactionHistoryPane;
