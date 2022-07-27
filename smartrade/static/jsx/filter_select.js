import React, { useContext, useEffect, useState } from 'react';

import { Dropdown } from 'semantic-ui-react';

import AppContext from "./app_context";

function FilterSelect({ title, name, options, defaultValue, onChange }) {
  const { account } = useContext(AppContext);
  const [selected, setSelected] = useState();

  useEffect(() => {
    changeFilter(defaultValue == null ? "" : defaultValue);
  }, [account]);

  function changeFilter(value) {
    setSelected(value);
    if (onChange) {
      onChange(name, value);
    }
  }
  
  return <Dropdown className="FilterSelect"
    placeholder={"Select " + title + "..."}
    header={title}
    selection
    value={selected}
    defaultValue={defaultValue}
    clearable
    options={Object.entries(options).map(([key, val]) => ({ value: val, text: key }))}
    onChange={(_, { value }) => changeFilter(value)}
  />;
}

export default FilterSelect;