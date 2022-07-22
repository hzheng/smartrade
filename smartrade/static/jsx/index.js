import React from 'react';
import ReactDOM from 'react-dom/client';

import { IntlProvider } from 'react-intl'

import App from './app';
import { getElementData } from './util';

import 'semantic-ui-css/semantic.min.css'
import '../sass/index.scss';

const root = document.getElementById('root');

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <IntlProvider locale="en">
      <App {...getElementData(root)} />
    </IntlProvider>
  </React.StrictMode>
);
