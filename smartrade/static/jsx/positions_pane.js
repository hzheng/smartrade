import React, { useEffect } from 'react';

import { Divider, Header, Segment } from 'semantic-ui-react'

import AccountSummaryPanel from './account_summary_panel';
import PositionsPanel from './positions_panel';

import './positions_pane.css';

function PositionsPane() {
  useEffect(() => {
    console.log("render PositionsPane");
  }, []);

  return (
    <Segment className="PositionsPane">
      <Header as='h3'>Summary</Header>

      <section className="summary">
        <AccountSummaryPanel />
      </section>

      <Divider section />

      <Header as='h3'>Positions</Header>

      <section className="positions">
        <PositionsPanel />
      </section>
    </Segment>
  )
}

export default PositionsPane;