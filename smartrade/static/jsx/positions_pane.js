import React, { useEffect } from 'react';

import AccountSummaryPanel from './account_summary_panel';
import PositionsPanel from './positions_panel';

import './positions_pane.css';

function PositionsPane() {
  useEffect(() => {
    console.log("render PositionsPane");
  }, []);

  return (
    <div className="PositionsPane">
      <section className="summary">
        <AccountSummaryPanel />
      </section>
      <section className="positions">
        <PositionsPanel />
      </section>
    </div >
  )
}

export default PositionsPane;