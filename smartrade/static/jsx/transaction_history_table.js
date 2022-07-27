import React, { useEffect, useReducer } from 'react';

import _ from 'lodash';
import { Table } from 'semantic-ui-react';

import { FormattedField } from './format';

function TransactionHistoryTable({ historyData }) {
  function reducer(state, action) {
    if (state.data.length == 0) { return state; }

    switch (action.type) {
      case 'SORT_BY_FIELD':
        if (state.column === action.column) {
          return {
            ...state,
            data: state.data.slice().reverse(),
            direction:
              state.direction === 'ascending' ? 'descending' : 'ascending',
          }
        }
        return {
          column: action.column,
          data: _.sortBy(state.data, [action.column]),
          direction: 'ascending',
        }
      default:
        throw new Error()
    }
  }

  function sortByColumn(col) {
    dispatch({ type: 'SORT_BY_FIELD', column: col });
  }

  useEffect(() => {
    tableState.data = historyData;
    sortByColumn('date');
  }, [historyData]);

  const [tableState, dispatch] = useReducer(reducer, {
    data: historyData,
    column: null,
    direction: null,
  })
  const { data, column, direction } = tableState;

  function getClasses(tx) {
    const isSliced = tx.slice_parent && tx.slice_parent != tx._id;
    const isMerged = tx.merge_parent && tx.merge_parent != tx._id && tx.merge_parent != tx.slice_parent
    const isVirtual = tx.merge_parent == tx._id || isSliced;
    const isEffective = !isMerged && (tx.slice_parent != tx._id);
    let classes = isEffective ? "effective" : "ineffective";
    if (isVirtual) {
      classes += " virtual";
    } else {
      classes += " original";
    }
    if (isMerged) {
      classes += " merged";
    }
    if (isSliced) {
      classes += " sliced";
    }
    if (tx.valid <= 0) {
      classes += (tx.valid == 0 ? ' ignored' : ' invalid');
    }
    if (tx.grouped) {
      classes += " completed";
    } else if (tx.grouped === false) {
      classes += " uncompleted";
    }
    return classes;
  }

  return (
    <Table sortable celled fixed className="history">
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>No.</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'date' ? direction : null}
            onClick={() => sortByColumn('date')} >Date</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'symbol' ? direction : null}
            onClick={() => sortByColumn('symbol')} >Symbol</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'action' ? direction : null}
            onClick={() => sortByColumn('action')} >Action</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'price' ? direction : null}
            onClick={() => sortByColumn('price')} >Price</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'quantity' ? direction : null}
            onClick={() => sortByColumn('quantity')} >Quantity</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'fee' ? direction : null}
            onClick={() => sortByColumn('fee')} >Fee</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'amount' ? direction : null}
            onClick={() => sortByColumn('amount')} >Amount</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'description' ? direction : null}
            onClick={() => sortByColumn('description')} >Description</Table.HeaderCell>
          <Table.HeaderCell sorted={column === 'tx_id' ? direction : null}
            onClick={() => sortByColumn('tx_id')} >Tx Id</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {
          data.map((tx, index) => (
            <Table.Row key={tx._id} className={getClasses(tx)}>
              <Table.Cell>{index + 1}</Table.Cell>
              <FormattedField value={tx.date} style="date" />
              <Table.Cell>{tx.symbol}</Table.Cell>
              <Table.Cell>{tx.action}</Table.Cell>
              <FormattedField value={tx.price} style="currency" />
              <Table.Cell>{tx.quantity}</Table.Cell>
              <FormattedField value={tx.fee} style="currency" />
              <FormattedField value={tx.amount} style="currency" />
              <Table.Cell>{tx.description}</Table.Cell>
              <Table.Cell>{tx.tx_id}</Table.Cell>
            </Table.Row>
          ))
        }
      </Table.Body>
      <Table.Footer>
        <Table.Row>
          <Table.HeaderCell colSpan='10'>{data.length} Results</Table.HeaderCell>
        </Table.Row>
      </Table.Footer>
    </Table>
  )
}

export default TransactionHistoryTable;
