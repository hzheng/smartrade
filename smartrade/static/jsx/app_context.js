import React from 'react';

const AppContext = React.createContext({ accountMap: {}, account: null, setAccount: () => {} });

export default AppContext;
