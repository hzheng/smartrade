import React, { useContext, useEffect, useState } from 'react';

import { FormattedField } from './format';

import AppContext from "./app_context";

function PositionItem({ position }) {
  return (
    <tr className="position">
      <td className="symbol">{position.symbol}</td>
      <td className="quantity">{position.quantity}</td>
      <FormattedField value={position.cost} style="currency" />
      <FormattedField value={position.price} style="currency" />
      <FormattedField value={position.day_gain} style="currency" />
      <FormattedField value={position.day_gain_percent} style="percent" />
      <FormattedField value={position.gain} style="currency" />
      <FormattedField value={position.gain_percent} style="percent" />
      <FormattedField value={position.value} style="currency" />
    </tr>
  );
}

function PositionsPanel() {
  const { account, load } = useContext(AppContext);
  const [equityPositions, setEquityPositions] = useState({ positions: [] });
  const [optionPositions, setOptionPositions] = useState({ positions: [] });

  function loadPositions(positions) {
    positions.sort((p, q) => p.symbol > q.symbol ? 1 : -1);
    const posArray = [{ positions: [] }, { positions: [] }]
    for (let i = 0; i < 2; i++) {
      let total_value = 0;
      const p = posArray[i];
      for (const pos of positions) {
        const symbol = pos.symbol;
        const isOption = symbol.indexOf("_") >= 0;
        if (isOption ^ (i > 0)) { continue; }

        const k = isOption ? 100 : 1;
        pos.day_gain_percent /= 100;
        const marketValue = pos.quantity * pos.price;
        pos.price /= k;
        total_value += marketValue;
        const totalCost = pos.cost * pos.quantity * k;
        const gain = marketValue - totalCost;
        pos['gain'] = gain;
        pos['gain_percent'] = gain / totalCost;
        pos['value'] = marketValue;
        p['positions'].push(pos);
      }
      p['total_value'] = total_value;
    }
    setEquityPositions(posArray[0]);
    setOptionPositions(posArray[1]);
  }

  useEffect(() => {
      load(`/account/${account}/positions`,
      data => { loadPositions(data); }, "positions");
  }, [account]);

  return (
    <div className="PositionsPanel">
      <table>
        <tbody>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
            <th>Cost</th>
            <th>Price</th>
            <th>Day Gain</th>
            <th>Day Gain(%)</th>
            <th>Gain</th>
            <th>Gain(%)</th>
            <th>Market value</th>
          </tr>
          <tr>
            <td className="label" colSpan="9">Equities</td>
          </tr>
          {
            equityPositions.positions.map((pos, index) => (<PositionItem position={pos} key={`equity${index}`} />))
          }
          <tr>
            <th colSpan="8">Total value</th>
            <FormattedField value={equityPositions.total_value} style="currency" />
          </tr>
          <tr>
            <td className="label" colSpan="9">Options</td>
          </tr>
          {
            optionPositions.positions.map((pos, index) => (<PositionItem position={pos} key={`option${index}`} />))
          }
          <tr>
            <th colSpan="8">Total value</th>
            <FormattedField value={optionPositions.total_value} style="currency" />
          </tr>
        </tbody>
      </table>
    </div >
  )
}

export default PositionsPanel;
