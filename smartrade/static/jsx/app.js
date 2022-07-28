import React, { useMemo, useState, useEffect } from 'react';

import { fetchData } from "./util";
import AppContext from "./app_context";
import AccountSelect from './account_select';
import MainPane from "./main_pane";
import StatusPanel from './status_panel';

function App({ accounts, default_account }) {
    const [account, setAccount] = useState(default_account);
    const accountMap = accounts.reduce((prev, cur) => {
        const [alias, acct] = cur.split(":");
        prev[alias] = acct;
        return prev;
    }, {});

    const [status, setStatus] = useState({});
    function load(url, onOk, target, options) {
        console.log("loading url:", url);
        setStatus({ type: 'progress', message: `Loading ${target}...` });
        fetchData(url, options,
            (data) => {
                setStatus({ type: 'ok', message: `Loaded ${target}.` });
                onOk(data);
            },
            (err) => {
                setStatus({ type: 'error', message: `Failed to load ${target}.`, detail: `Reason: ${err}` });
            },
            (err) => {
                setStatus({ type: 'error', message: `No response for ${target}.`, detail: `Please Check your network. Reason: ${err}` });
            }
        );
    }

    const context = useMemo(() => ({ accountMap, account, setAccount, load }), [account]);
    const changeAccount = (acct) => { setAccount(acct) };

    useEffect(() => {
        console.log("current account :", context.account);
    });

    return (<div className="app">
        <AppContext.Provider value={context}>
            <div className="app-menu">
                <AccountSelect onAccountChange={changeAccount} />
            </div>
            <div className="app-status">
                <StatusPanel {...status} />
            </div>
            <div className='app-main'>
                <MainPane />
            </div>
        </AppContext.Provider>
    </div>);
}

export default App;
