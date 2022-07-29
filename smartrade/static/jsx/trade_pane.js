import React from 'react';

import { Tab } from 'semantic-ui-react';

import OrderStatusPane from "./order_status_pane"
import SavedOrdersPane from "./saved_orders_pane"
import PlaceOrderPane from "./place_order_pane"

function TradePane({ activeIndices, setActiveIndex }) {
  const panes = [
    { menuItem: "Order Status", render: () => <Tab.Pane><OrderStatusPane /></Tab.Pane> },
    { menuItem: "Saved Orders", render: () => <Tab.Pane><SavedOrdersPane /></Tab.Pane> },
    { menuItem: "Place Order", render: () => <Tab.Pane><PlaceOrderPane /></Tab.Pane> },
  ];

  const changeTab = (_, { activeIndex }) => {
    setActiveIndex("Trade", activeIndex);
  };

  return <Tab menu={{ secondary: true }} panes={panes} defaultActiveIndex={activeIndices['Trade'] || 0} onTabChange={changeTab} />;
}

export default TradePane;
