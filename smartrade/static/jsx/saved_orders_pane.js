import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function SavedOrdersPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("Rendering SavedOrdersPane for account:", account);
  }, [account]);

  return (
    <div>TODO: saved orders content for {account}</div>
  )
}

export default SavedOrdersPane;
