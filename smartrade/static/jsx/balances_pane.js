import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function BalancesPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("BalancesPane account is ", account);
  }, [account]);

  return (
    <div>TODO: balance content for {account}</div>
  )
}

export default BalancesPane;