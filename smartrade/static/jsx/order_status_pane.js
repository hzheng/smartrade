import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function OrderStatusPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("OrderStatusPane account is ", account);
  }, [account]);

  return (
    <div>TODO: order status content for {account}</div>
  )
}

export default OrderStatusPane;
