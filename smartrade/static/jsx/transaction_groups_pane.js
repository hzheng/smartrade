import React, { useContext, useEffect, useState } from 'react';

import { Checkbox, Divider, Header, Segment } from 'semantic-ui-react';

import AppContext from "./app_context";
import TickersSelect from './tickers_select';
import TransactionGroupsSummaryPanel from './transaction_groups_summary_panel';
import TransactionGroupsPanel from './transaction_groups_panel';

import './transaction_groups_pane.scss';

function TransactionGroupsPane() {
  const { account, load } = useContext(AppContext);

  const [tickers, setTickers] = useState([]);
  const [showCompleted, toggleCompleted] = useState(false);
  const [summary, setSummary] = useState([{}, null]);
  const [groupData, setGroupData] = useState({});

  useEffect(() => {
    if (tickers.length == 0) {
      setSummary([{}, null]);
      setGroupData({});
      return;
    }
    const tickerList = tickers.join(",");
    load(`/account/${account}/transaction_groups/${tickerList}`,
      data => {
        setGroupData(data);
        const summaryData = {};
        const totalData = [0, 0];
        for (const [ticker, { investment, profit }] of Object.entries(data)) {
          totalData[0] += investment;
          totalData[1] += profit;
          summaryData[ticker] = [investment, profit]
        }
        setSummary([summaryData, totalData]);
      }, `transaction groups(${tickerList})`);
  }, [account, tickers]);

  return (
    <Segment className="TransactionGroupsPane">
      <TickersSelect onChange={(t) => setTickers(t)} />
      <Checkbox label="Show completed" onChange={(_, { checked }) => toggleCompleted(checked)} />

      <Divider />
      <Header as='h3'>Summary</Header>
      <TransactionGroupsSummaryPanel summary={summary[0]} total={summary[1]} />

      <Header as='h3'>Transactions</Header>
      {
        Object.entries(groupData).map(([ticker, groupInfo], index) => (
          <React.Fragment key={`txGroups-${index}`}>
            <Divider />
            <Header as='h4'>{ticker}</Header>
            <TransactionGroupsPanel groupInfo={groupInfo} showCompleted={showCompleted} />
          </React.Fragment>
        ))
      }
    </Segment>
  )
}

export default TransactionGroupsPane;
