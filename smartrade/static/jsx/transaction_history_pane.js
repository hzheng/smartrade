import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function TransactionHistoryPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("TransactionHistoryPane account is ", account);
  }, [account]);

  return (
    <div>TODO: TransactionHistory content for {account}</div>
  )
}

export default TransactionHistoryPane;
