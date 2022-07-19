import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function TransactionGroupsPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("TransactionGroupsPane account is ", account);
  }, [account]);

  return (
    <div>TODO: TransactionGroup content for {account}</div>
  )
}

export default TransactionGroupsPane;
