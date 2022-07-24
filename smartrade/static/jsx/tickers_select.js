import React, { useContext, useEffect, useState } from 'react';

import { Dropdown } from 'semantic-ui-react';

import AppContext from "./app_context";
import { fetchData } from "./util";

function TickersSelect({ onTickersChange }) {
  const { account } = useContext(AppContext);

  const [selectedOptions, setOptions] = useState([]);
  const [tickersOptions, setTickersOptions] = useState([]);

  useEffect(() => {
    changeTickers([]);
    fetchData(`/account/${account}/traded_tickers`,
      data => {
        const options = Object.entries(data).map(
          ([ticker, open]) => ({ key: ticker, value: ticker, text: (open ? "*" : "") + ticker }));
        setTickersOptions(options);
      });
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