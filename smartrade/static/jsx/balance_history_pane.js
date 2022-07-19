import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function BalanceHistoryPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("BalancesHistoryPane account is ", account);
  }, [account]);

  return (
    <div>TODO: Balance history content for {account}</div>
  )
}

export default BalanceHistoryPane;