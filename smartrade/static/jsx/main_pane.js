import React, { useState, useEffect } from 'react';

import { Tab } from 'semantic-ui-react';

import AccountPane from "./account_pane";
import TransactionPane from "./transaction_pane";
import TradePane from "./trade_pane";

function MainPane(props) {
    const menu = { Account: AccountPane, Transaction: TransactionPane, Trade: TradePane };

    const [activeIndices] = useState({});
    const setActiveIndex = (title, index) => { activeIndices[title] = index; }

    const extendedProps = { ...props, activeIndices, setActiveIndex };
    const panes = Object.entries(menu).map(
        ([title, MenuPane]) => ({ menuItem: title, render: () => <Tab.Pane><MenuPane {...extendedProps} /></Tab.Pane> }));

    return <Tab panes={panes} defaultActiveIndex={0} />;
}

export default MainPane;
