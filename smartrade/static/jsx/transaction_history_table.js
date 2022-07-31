import React, { useEffect } from 'react';

import { Table } from 'semantic-ui-react';

import { FormattedField } from './format';
import SortedTable from './sorted_table';

function TransactionHistoryTable({ historyData }) {
  useEffect(() => {
    console.log("Rendering TransactionHistoryTable");
  }, [historyData]);

  function TableBody({ data }) {
    return (
      <>
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
      </>
    );
  }

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

  const columns = [
    ['no.', 'No.', false],
    ['date', 'Date', true],
    ['symbol', 'Symbol', true],
    ['action', 'Action', true],
    ['price', 'Price', true],
    ['quantity', 'Quantity', true],
    ['fee', 'Fee', true],
    ['amount', 'Amount', true],
    ['description', 'Description', true],
    ['tx_id', 'Tx Id', true]
  ]

  return (
    <SortedTable tableData={historyData} columns={columns} name="txHistoryTable" celled fixed className="history">
      <TableBody />
    </SortedTable>
  )
}

export default TransactionHistoryTable;
