import React from 'react';
import { createRoot } from 'react-dom/client';

import { IntlProvider } from 'react-intl'

import App from './app';
import { getElementData } from './util';

import 'semantic-ui-css/semantic.min.css'
import '../sass/index.scss';

const rootElement = document.getElementById('root');

createRoot(rootElement).render(
  <React.StrictMode>
    <IntlProvider locale="en">
      <App {...getElementData(root)} />
    </IntlProvider>
  </React.StrictMode>
);
