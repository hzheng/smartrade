import React, { useContext, useEffect, useState } from 'react';

import { Checkbox, Divider, Header, Segment } from 'semantic-ui-react';

import AppContext from "./app_context";
import TickersSelect from './tickers_select';
import TransactionGroupsPanel from './transaction_groups_panel';

import './transaction_groups_pane.css';

function TransactionGroupsPane() {
  const { account } = useContext(AppContext);

  const [tickers, setTickers] = useState([]);
  const [showCompleted, toggleCompleted] = useState(false);

  useEffect(() => {
    console.log("TransactionGroupsPane account is ", account);
  }, [account]);

  return (
    <Segment className="TransactionGroupsPane">
      <TickersSelect onTickersChange={(t) => setTickers(t)} />
      <Checkbox label="Show completed" onChange={(_, { checked }) => toggleCompleted(checked)} />

      <Header as='h3'>Transactions</Header>
      {
        tickers.map((ticker, index) => (
          <React.Fragment key={`txGroups-${index}`}>
            <TransactionGroupsPanel ticker={ticker} showCompleted={showCompleted} />
          </React.Fragment>
        ))
      }
    </Segment>
  )
}

export default TransactionGroupsPane;
