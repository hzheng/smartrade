import React, { useContext, useEffect } from 'react';

import { FormattedDate, FormattedNumber } from 'react-intl';

import AppContext from './app_context';

import './ticker_transaction_groups_panel.css';

function SymbolTransactionPanel({ transaction }) {
  const isOpen = !!transaction.symbol;
  return (
    <tr className={isOpen ? 'open' : 'close'}>
      {isOpen &&
        <td className="symbol" rowSpan="100">{transaction.symbol}</td>
      }
      <td className="date"><FormattedDate value={transaction.date} day="2-digit" month="2-digit" year="numeric" /></td>
      <td>{transaction.action}</td>
      <td className="money amount"><FormattedNumber value={transaction.price} style="currency" currency="USD" /></td>
      <td className="quantity">{transaction.quantity}</td>
      <td className="money amount"><FormattedNumber value={transaction.fee} style="currency" currency="USD" /></td>
      <td className="money amount"><FormattedNumber value={transaction.amount} style="currency" currency="USD" /></td>
    </tr>
  );
}

function TransactionGroupPanel({ groupTransaction, isFirst }) {
  return (
    <table className="transaction">
      <colgroup>
        <col span="1" style={{ width: '25%' }} />
        <col span="1" style={{ width: '15%' }} />
        <col span="1" style={{ width: '10%' }} />
        <col span="1" style={{ width: '10%' }} />
        <col span="1" style={{ width: '10%' }} />
        <col span="1" style={{ width: '10%' }} />
        <col span="1" style={{ width: '20%' }} />
      </colgroup>
      {isFirst &&
        <tr name="header">
          <th>Symbol</th>
          <th>Date</th>
          <th>Action</th>
          <th>Price</th>
          <th>Quantity</th>
          <th>Fee</th>
          <th>Amount</th>
        </tr>
      }
      {
        groupTransaction.map((symbolTx) => (
          <SymbolTransactionPanel transaction={symbolTx} />
        ))
      }
    </table>
  );
}

function TickerTransactionGroupsPanel({ chains, completed, showCompleted, ...props }) {
  const { account } = useContext(AppContext);

  useEffect(() => {
  }, [account]);

  const classAttr = { className: `TickerTransactionGroupsPanel${completed ? ' completed' : ''}` };
  return (
    (showCompleted || !completed) &&
    <section {...classAttr}>
      {
        chains.map((groupTx, index) => (<TransactionGroupPanel groupTransaction={groupTx} isFirst={index == 0} />))
      }
      <div className="summary">
        <label>Profit:</label>
        <span className="money amount"><FormattedNumber value={props.profit} style="currency" currency="USD" /></span>
        <label>ROI:</label>
        <span className="amount"><FormattedNumber value={props.roi} style='percent' minimumFractionDigits={2} /></span>
        <label>Cost:</label>
        <span className="money amount"><FormattedNumber value={props.cost} style="currency" currency="USD" /></span>
        <label>Duration:</label>
        <span className="duration">{props.duration}</span> day(s)
      </div>
    </section>
  )
}

export default TickerTransactionGroupsPanel;
