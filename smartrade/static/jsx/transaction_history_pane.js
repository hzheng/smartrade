import React, { useContext, useEffect, useState } from 'react';

import { Button, Header, Icon, Message, Segment } from 'semantic-ui-react';

import { FormattedField } from './format';
import AppContext from "./app_context";
import TickersSelect from './tickers_select';
import DateRangeSelect from './date_range_select';
import FilterSelect from './filter_select';

import './transaction_history_pane.css';

function TransactionFilterPanel({ filters, onCommand }) {
  function update(name, value) {
    filters[name] = value;
  }

  return <div className="TransactionFilterPanel">
    <div>
      <TickersSelect onChange={(t) => update('tickers', t)} />
      <Button icon="search" content="Search" onClick={() => onCommand(filters)} />
    </div>
    <div>
      <DateRangeSelect onChange={(range) => update('dateRange', range)} />
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
  const [dateOrder, setDateOrder] = useState(0);
  const [historyData, setHistoryData] = useState([]);

  function search(values) {
    setFilters(values);
    const { tickers, ...options } = values;
    const tickerList = tickers && tickers.length ? tickers.join(",") : "all";
    const params = Object.entries(options).map(([key, val]) => (val === "" || val == null) ? "" : `${key}=${val}`);
    const url = `/account/${account}/transactions/${tickerList}?${params.join('&')}`;
    load(url, data => { setHistoryData(data); }, `transaction history(${tickerList})`);
  }

  function toggleDateOrder() {
    const newOrder = dateOrder ^ 1;
    setDateOrder(newOrder);
    filters['dateOrder'] = newOrder;
    search(filters);
  }

  useEffect(() => {
    console.log("history render");
    setHistoryData([]);
  }, [account, filters]);

  function getClasses(tx) {
    const isSliced = tx.slice_parent && tx.slice_parent != tx._id;
    const isMerged = tx.merge_parent && tx.merge_parent != tx._id && tx.merge_parent != tx.slice_parent
    const isVirtual = tx.merge_parent == tx._id || isSliced;
    const isEffective = !isMerged && (tx.slice_parent != tx._id);
    let classes = isEffective ? "effective" : "ineffective";
    if (isVirtual) {
      classes += " virtual";
    } else {
      classes += " original";
    }
    if (isMerged) {
      classes += " merged";
    }
    if (isSliced) {
      classes += " sliced";
    }
    if (tx.valid <= 0) {
      classes += (tx.valid == 0 ? ' ignored' : ' invalid');
    }
    if (tx.grouped) {
      classes += " completed";
    } else if (tx.grouped === false) {
      classes += " uncompleted";
    }
    return classes;
  }

  return (
    <Segment className="TransactionHistoryPane">
      <TransactionFilterPanel filters={filters} onCommand={search} />
      <TransactionSummaryPanel />
      <Header as='h3'>{historyData.length} Result(s)</Header>
      <table className="history">
        <thead>
          <tr>
            <th>No.</th>
            <th>Date<Icon name={`caret ${dateOrder == 1 ? 'up' : 'down'}`} onClick={toggleDateOrder} /></th>
            <th>Symbol</th>
            <th>Action</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Fee</th>
            <th>Amount</th>
            <th>Description</th>
            <th>Tx Id</th>
          </tr>
        </thead>
        <tbody>
          {
            historyData.map((tx, index) => (
              <React.Fragment key={`txHistory-${index}`}>
                <tr className={getClasses(tx)}>
                  <td>{index + 1}</td>
                  <FormattedField value={tx.date} style="date" />
                  <td>{tx.symbol}</td>
                  <td>{tx.action}</td>
                  <FormattedField value={tx.price} style="currency" />
                  <td>{tx.quantity}</td>
                  <FormattedField value={tx.fee} style="currency" />
                  <FormattedField value={tx.amount} style="currency" />
                  <td>{tx.description}</td>
                  <td>{tx.tx_id}</td>
                </tr>
              </React.Fragment>
            ))
          }
        </tbody>
      </table>
    </Segment>
  )
}

export default TransactionHistoryPane;
