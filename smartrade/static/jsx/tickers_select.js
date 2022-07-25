import React, { useContext, useEffect, useState } from 'react';

import { Dropdown } from 'semantic-ui-react';

import AppContext from "./app_context";

function TickersSelect({ onTickersChange }) {
  const { account, load } = useContext(AppContext);

  const [selectedOptions, setOptions] = useState([]);
  const [tickersOptions, setTickersOptions] = useState([]);

  useEffect(() => {
    changeTickers([]);
    load(`/account/${account}/traded_tickers`,
      data => {
        const options = Object.entries(data).map(
          ([ticker, open]) => ({ key: ticker, value: ticker, text: (open ? "*" : "") + ticker }));
        setTickersOptions(options);
      }, "traded tickers");
  }, [account]);

  function changeTickers(value) {
    setOptions(value);
    onTickersChange(value);
  }

  return (
    <Dropdown className="TickersSelect"
      placeholder="Select ticker(s)"
      clearable
      multiple
      search
      selection
      options={tickersOptions}
      value={selectedOptions}
      onChange={(_, { value }) => changeTickers(value)}
    />
  ); // onChange => onClose?
}

export default TickersSelect;