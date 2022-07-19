import React, { useContext, useEffect } from 'react';

import AppContext from "./app_context";

function SavedOrderPane() {
  const { account } = useContext(AppContext);

  useEffect(() => {
    console.log("SavedOrderPane account is ", account);
  }, [account]);

  return (
    <div>TODO: saved order content for {account}</div>
  )
}

export default SavedOrderPane;
