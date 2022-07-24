import React from 'react';

import { Tab } from 'semantic-ui-react';

import TransactionGroupsPane from "./transaction_groups_pane"
import TransactionHistoryPane from "./transaction_history_pane"

function TransactionPane({ activeIndices, setActiveIndex }) {
  const panes = [
    { menuItem: "Transaction Groups", render: () => <Tab.Pane><TransactionGroupsPane /></Tab.Pane> },
    { menuItem: "Transaction History", render: () => <Tab.Pane><TransactionHistoryPane /></Tab.Pane> },
  ];

  const changeTab = (_, { activeIndex }) => {
    setActiveIndex("Transaction", activeIndex);
  };

  return <Tab menu={{ secondary: true }} panes={panes} defaultActiveIndex={activeIndices['Transaction'] || 0} onTabChange={changeTab} />;
}

export default TransactionPane;