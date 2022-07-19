import React, { useMemo, useState, useEffect } from 'react';

import AppContext from "./app_context";
import AccountSelect from './account_select';
import MainPane from "./main_pane";

function App({ accounts, default_account }) {
    const [account, setAccount] = useState(default_account);
    const accountMap = accounts.reduce((prev, cur) => {
        const [alias, acct] = cur.split(":");
        prev[alias] = acct;
        return prev;
    }, {});

    const context = useMemo(() => ({ accountMap, account, setAccount }), [account]);
    const changeAccount = (acct) => { setAccount(acct) };

    useEffect(() => {
        console.log("current account :", context.account);
    });

    return (<div className="app">
        <AppContext.Provider value={context}>
            <div className="app-menu">
                <AccountSelect onAccountChange={changeAccount} />
            </div>
            <div className='app-main'>
                <MainPane />
            </div>
        </AppContext.Provider>
    </div>);
}

export default App;
