import React, { useContext, useEffect, useState } from 'react';

import { Icon, Loader, Popup } from 'semantic-ui-react';

import AppContext from './app_context';

import './status_panel.css'

function StatusPanel({ type, message, detail }) {
  const { account } = useContext(AppContext);

  const [statusType, setType] = useState("");

  useEffect(() => {
    setType(type);
    switch (type) {
      case 'progress':
        break;
      case 'ok':
        setTimeout(() => setType(""), 5000);
        break;
      case 'error':
        setTimeout(() => setType(""), 30000);
        break;
    }
  }, [account, type, message]);

  return (
    <div className={`StatusPanel ${type}`}>
      {
        {
          '': "",
          'progress': <><Loader active inline /><span>{message}</span></>,
          'ok': <span><Icon name='info circle' />{message}</span>,
          'error': <Popup trigger={<span><Icon name='warning sign' />{message}</span>} position="right center">
            {detail}
          </Popup>
        }[statusType]
      }
    </div>
  );
}

export default StatusPanel;