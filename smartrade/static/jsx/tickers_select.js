import React, { useContext, useEffect, useState } from 'react';

import { Dropdown } from 'semantic-ui-react';

import AppContext from "./app_context";

function TickersSelect({ onChange }) {
  const { account, load } = useContext(AppContext);

  const [selectedOptions, setOptions] = useState([]);
  const [tickersOptions, setTickersOptions] = useState([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    changeTickers([]);
    load(`/account/${account}/traded_tickers`,
      data => {
        const options = Object.entries(data).map(
          ([ticker, open]) => ({ key: ticker, value: ticker, text: (open ? "*" : "") + ticker }));
        setTickersOptions(options);
        setLoaded(true);
      }, "traded tickers");
  }, [account]);

  function changeTickers(value) {
    setOptions(value);
    if (onChange) {
      onChange(value);
    }
  }

  return (
    <Dropdown className="TickersSelect"
      placeholder="Select ticker(s)"
      header="ticker(s)"
      clearable
      multiple
      search
      selection
      loading={!loaded}
      options={tickersOptions}
      value={selectedOptions}
      onChange={(_, { value }) => changeTickers(value)}
    />
  ); // onChange => onClose?
}

export default TickersSelect;