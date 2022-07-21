import React, { useContext, useEffect } from 'react';

import $ from 'jquery';

import AppContext from "./app_context";
import { fetchData, resetValues, setValue } from "./util";

function PositionsPanel() {
  const { account } = useContext(AppContext);

  function loadPositions(positions, $self) {
    positions.sort((p, q) => p.symbol > q.symbol ? 1 : -1);

    const $stock_position = $('tr[name="stock_position"]', $self);
    $stock_position.not(':last').remove();
    const $option_position = $('tr[name="option_position"]', $self);
    $option_position.not(':last').remove();
    const $rows = $('tr.position', $self);
    const $total = $('td[name="total_value"]', $self);
    for (let i = 0; i < 2; i++) {
      const $row = $rows.eq(i);
      let total_value = 0;
      for (const pos of positions) {
        const symbol = pos.symbol;
        const isOption = symbol.indexOf("_") >= 0;
        if (isOption ^ (i > 0)) { continue; }

        const $newRow = $row.clone().insertBefore($row);
        const k = isOption ? 100 : 1;
        setValue($("td[name='symbol']", $newRow), symbol);
        setValue($("td[name='quantity']", $newRow), pos.quantity);
        setValue($("td[name='cost']", $newRow), pos.cost);
        setValue($("td[name='price']", $newRow), pos.price / k);
        setValue($("td[name='day_gain']", $newRow), pos.day_gain);
        setValue($("td[name='day_gain_percent']", $newRow), pos.day_gain_percent / 100);
        const marketValue = pos.quantity * pos.price;
        total_value += marketValue;
        const totalCost = pos.cost * pos.quantity * k;
        const gain = marketValue - totalCost;
        setValue($("td[name='gain']", $newRow), gain);
        setValue($("td[name='gain_percent']", $newRow), gain / totalCost);
        setValue($("td[name='value']", $newRow), marketValue);
        $newRow.show();
      }
      setValue($total.eq(i), total_value);
    }
  }

  useEffect(() => {
    const $self = $(".PositionsPanel");
    resetValues($self, "???");
    (async () => {
      const res = await fetchData(`/account/${account}/positions`);
      const data = await res.json();
      loadPositions(data.positions, $self);
    })();
  }, [account]);

  return (
    <div className="PositionsPanel">
      <table>
        <tbody>
          <tr>
            <th>Symbol</th>
            <th>Quanity</th>
            <th>Cost</th>
            <th>Price</th>
            <th>Day Gain</th>
            <th>Day Gain(%)</th>
            <th>Gain</th>
            <th>Gain(%)</th>
            <th>Market value</th>
          </tr>
          <tr>
            <td className="label" colSpan="9">Stocks</td>
          </tr>
          <tr className="position" name="stock_position" style={{ display: 'none' }}>
            <td className="symbol" name="symbol"></td>
            <td className="quantity" name="quantity"></td>
            <td className="money amount" name="cost"></td>
            <td className="money amount" name="price"></td>
            <td className="money amount" name="day_gain"></td>
            <td className="amount percent" name="day_gain_percent"></td>
            <td className="money amount" name="gain"></td>
            <td className="amount percent" name="gain_percent"></td>
            <td className="money amount" name="value"></td>
          </tr>
          <tr>
            <th colSpan="8">Total value</th>
            <td className="money amount" name="total_value"></td>
          </tr>
          <tr>
            <td className="label" colSpan="9">Options</td>
          </tr>
          <tr className="position" name="option_position" style={{ display: 'none' }}>
            <td className="symbol" name="symbol"></td>
            <td className="quantity" name="quantity"></td>
            <td className="money amount" name="cost"></td>
            <td className="money amount" name="price"></td>
            <td className="money amount" name="day_gain"></td>
            <td className="amount percent" name="day_gain_percent"></td>
            <td className="money amount" name="gain"></td>
            <td className="amount percent" name="gain_percent"></td>
            <td className="money amount" name="value"></td>
          </tr>
          <tr>
            <th colSpan="8">Total value</th>
            <td className="money amount" name="total_value"></td>
          </tr>
        </tbody>
      </table>
    </div >
  )
}

export default PositionsPanel;
