import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function WatchListsPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("WatchListPane account is ", account);
  }, [account]);

  return (
    <div>TODO: watch lists content for {account}</div>
  )
}

export default WatchListsPane;