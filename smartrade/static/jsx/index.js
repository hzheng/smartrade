import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './app';
import { get_data } from './util';

import 'semantic-ui-css/semantic.min.css'
import '../sass/index.scss';

const root = document.getElementById('root');

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <App {...get_data(root)} />
  </React.StrictMode>
);
