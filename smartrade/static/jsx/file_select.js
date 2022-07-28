import React, { useContext, useEffect, useRef, useState } from 'react';

import { Button, Form, Message } from 'semantic-ui-react';

import AppContext from './app_context';

function FileSelect({ title, icon, validate, onSubmit }) {
  const { account } = useContext(AppContext);
  const [message, setMessage] = useState();
  const fileInput = useRef(null);

  useEffect(() => {
    console.log("Rendering FileSelect for account:", account);
    setMessage("");
  }, [account]);

  function handleFileInput(e) {
    const file = e.target.files[0];
    console.log("handling file input", file);
    if (validate) {
      const error = validate(file);
      setMessage(error);
      if (error) { return; }
    }
    const formData = new FormData();
    formData.append('file', file);
    onSubmit({ method: 'POST', body: formData });
  }

  return (
    <Form className="FileSelect">
      <Form.Field>
        <Button
          content={title}
          labelPosition="left"
          icon={icon}
          onClick={_ => fileInput.current && fileInput.current.click()}
        />
        <input type="file" style={{ display: "none" }} ref={fileInput} onChange={handleFileInput} />
      </Form.Field>
      {message && (<Message negative>{message}</Message>)}
    </Form>
  );
}

export default FileSelect;