import React from 'react';

import { Tab } from 'semantic-ui-react';

import PositionsPane from "./positions_pane";
import BalancesPane from "./balances_pane";
import BalanceHistoryPane from "./balance_history_pane";
import WatchListsPane from "./watch_lists_pane";

function AccountPane({ activeIndices, setActiveIndex }) {
  const panes = [
    { menuItem: "Positions", render: () => <Tab.Pane><PositionsPane /></Tab.Pane> },
    { menuItem: "Balances", render: () => <Tab.Pane><BalancesPane /> </Tab.Pane> },
    { menuItem: "Balance History", render: () => <Tab.Pane><BalanceHistoryPane /> </Tab.Pane> },
    { menuItem: "Watch Lists", render: () => <Tab.Pane><WatchListsPane /> </Tab.Pane> },
  ];
  
  const changeTab = (e, { activeIndex }) => {
    setActiveIndex("Account", activeIndex);
  };

  return <Tab menu={{ secondary: true }} panes={panes} defaultActiveIndex={activeIndices['Account'] || 0} onTabChange={changeTab} />;
}

export default AccountPane;