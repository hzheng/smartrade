import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function PlaceOrderPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("PlaceOrderPane account is ", account);
  }, [account]);

  return (
    <div>TODO: place order content for {account}</div>
  )
}

export default PlaceOrderPane;
