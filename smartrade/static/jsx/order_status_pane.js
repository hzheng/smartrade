import React, { useContext, useEffect, useState } from 'react';

import { Message } from 'semantic-ui-react';

import AppContext from "./app_context";

import OrderStatusTable from './order_status_table';

import './order_status_pane.scss';

function OrderStatusPane() {
  const { account, load } = useContext(AppContext);
  const [orderData, setOrderData] = useState([]);

  useEffect(() => {
    console.log("Rendering OrderStatusPane for account:", account);
    loadOrders();
  }, [account]);

  function setData(data) {
    for (const order of data) {
      const leg = order['legs'][0];
      order['ticker'] = leg['symbol'].split("_")[0];
      order['action'] = -leg['action'].charCodeAt(2); // open comes before close
    }
    setOrderData(data);
  }

  function loadOrders() {
    const url = `/account/${account}/orders`;
    load(url, data => { setData(data); }, "order status");
  }

  return (
    <div className="OrderStatusPane">
      <Message>Total orders: {orderData.length}</Message>
      {orderData.length > 0 && <OrderStatusTable statusData={orderData} />}
    </div>
  );
}

export default OrderStatusPane;
