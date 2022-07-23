import React, { useContext, useEffect, useState } from 'react';

import AppContext from './app_context';
import { fetchData } from './util';
import TickerTransactionGroupsPanel from './ticker_transaction_groups_panel';

function TransactionGroupsPanel({ ticker, showCompleted }) {
  const { account } = useContext(AppContext);

  const [txGroups, setTxGroups] = useState([]);

  useEffect(() => {
    (async () => {
      const res = await fetchData(`/account/${account}/transaction_groups/${ticker}`);
      const { transactionGroups } = await res.json();
      setTxGroups(transactionGroups);
    })();
  }, [account]);

  return (
    <div className="TransactionGroupsPanel">
      <div>Transations for {ticker}</div>
      {
        txGroups.map((group, index) => (
          <TickerTransactionGroupsPanel key={`tickerTxGroup-${index}`} {...group} showCompleted={showCompleted} />
        ))
      }
    </div >
  );
}

export default TransactionGroupsPanel;
