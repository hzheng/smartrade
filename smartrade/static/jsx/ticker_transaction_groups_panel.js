import React, { useContext, useEffect } from 'react';

import { FormattedField } from './format';

import AppContext from './app_context';

import './ticker_transaction_groups_panel.scss';

function SymbolTransactionPanel({ transaction }) {
  const isOpen = !!transaction.symbol;
  return (
    <tr className={isOpen ? 'open' : 'close'}>
      {isOpen &&
        <td className="symbol" rowSpan="100">{transaction.symbol}</td>
      }
      <FormattedField value={transaction.date} style="date" />
      <td>{transaction.action}</td>
      <FormattedField value={transaction.price} style="currency" />
      <td className="quantity">{transaction.quantity}</td>
      <FormattedField value={transaction.fee} style="currency" />
      <FormattedField value={transaction.amount} style="currency" />
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
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Date</th>
            <th>Action</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Fee</th>
            <th>Amount</th>
          </tr>
        </thead>
      }
      <tbody>
        {
          groupTransaction.map((symbolTx, index) => (
            <SymbolTransactionPanel key={`symbolTx-${index}`} transaction={symbolTx} />
          ))
        }
      </tbody>
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
        chains.map((groupTx, index) => (<TransactionGroupPanel key={`txGroup-${index}`} groupTransaction={groupTx} isFirst={index == 0} />))
      }
      <div className="summary">
        <label>Profit:</label>
        <FormattedField tag="span" value={props.profit} style="currency" />
        <label>ROI:</label>
        <FormattedField tag="span" value={props.roi} style="percent" />
        <label>Cost:</label>
        <FormattedField tag="span" value={props.cost} style="currency" />
        <label>Duration:</label>
        <span className="duration">{props.duration}</span> day(s)
      </div>
    </section>
  )
}

export default TickerTransactionGroupsPanel;
