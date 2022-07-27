import React, { useContext, useEffect, useState } from 'react';

import { Dropdown, Input } from 'semantic-ui-react';

import AppContext from "./app_context";

function DateInput({ onChange }) {
  return <Input type="date" onChange={(_, { value }) => onChange(value)} />;
}

function DateRangeSelect({ onChange }) {
  const { account } = useContext(AppContext);
  const [selected, setSelected] = useState();
  const [custom, setCustom] = useState(false);
  const [customRange] = useState(["", ""]);

  const customValue = ",";
  const options = [
    { value: "w-0", text: "this week" },
    { value: "m-0", text: "this month" },
    { value: "y-0", text: "this year" },
    { value: "w-1", text: "last week" },
    { value: "m-1", text: "last month" },
    { value: "y-1", text: "last year" },
    { value: customValue, text: "custom date range" }
  ]

  useEffect(() => {
    changeDate(null);
  }, [account]);

  function changeCustomDate(value, index) {
    customRange[index] = value;
    if (onChange) {
      onChange(customRange.join(","));
    }
  }

  function changeDate(value) {
    const useCustom = (value == customValue);
    setCustom(useCustom);
    setSelected(value);
    if (onChange) {
      onChange(useCustom ? customRange.join(",") : value);
    }
  }

  return (
    <div className="DateRangeSelect">
      <Dropdown
        placeholder="Select date range"
        header="date range"
        clearable
        options={options}
        value={selected}
        selection
        onChange={(_, { value }) => changeDate(value)}
      />
      <span style={{ visibility: custom ? "visible" : "hidden" }}>
        &nbsp;<DateInput onChange={(val) => changeCustomDate(val, 0)} />
        - <DateInput onChange={(val) => changeCustomDate(val, 1)} />
      </span>
    </div>
  );
}

export default DateRangeSelect;