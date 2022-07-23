import React, { useContext } from 'react';

import { Form } from 'semantic-ui-react';

import AppContext from "./app_context";

import './account_select.css';

function AccountSelect({ onAccountChange }) {
  const { accountMap, account } = useContext(AppContext);
  const options = Object.entries(accountMap).map(
    ([alias, acct]) => ({ value: acct, text: alias + " - #" + acct }));

  return (
    <Form className="AccountSelect">
      <Form.Dropdown
        selection
        label="Account:"
        icon="user"
        defaultValue={account}
        options={options}
        onChange={(_, { value }) => onAccountChange(value)}
      />
    </Form>);
}

export default AccountSelect;