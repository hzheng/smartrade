import React, { useContext, useEffect } from 'react';

import $ from 'jquery';

import AppContext from './app_context';

import './ticker_transaction_groups_panel.css';

function SymbolTransactionPanel({ transaction }) {
  const isOpen = !!transaction.symbol;
  return (
    <tr className={isOpen ? 'open' : 'close'}>
      {isOpen &&
        <td name="symbol" className="symbol" rowSpan="100">{transaction.symbol}</td>
      }
      <td name="date" className="date">{transaction.date}</td>
      <td name="action">{transaction.action}</td>
      <td name="price" className="money amount">{transaction.price}</td>
      <td name="quantity" className="quantity">{transaction.quantity}</td>
      <td name="fee" className="money amount">{transaction.fee}</td>
      <td name="amount" className="money amount">{transaction.amount}</td>
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
    const $self = $(".TransactionGroupsPanel");
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
        <span name="profit" className="money amount">{props.profit}</span>
        <label>ROI:</label>
        <span name="roi" className="amount percent">{props.roi}</span>
        <label>Cost:</label>
        <span name="cost" className="money amount">{props.cost}</span>
        <label>Duration:</label>
        <span name="duration" className="duration">{props.duration}</span> day(s)
      </div>
    </section>
  )
}

export default TickerTransactionGroupsPanel;
