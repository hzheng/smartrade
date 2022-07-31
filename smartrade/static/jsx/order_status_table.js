import React, { useEffect } from 'react';

import { Table } from 'semantic-ui-react';

import { FormattedField } from './format';
import SortedTable from './sorted_table';

function OrderStatusTable({ statusData }) {
  useEffect(() => {
    console.log("Rendering OrderStatusTable");
  }, [statusData]);

  function TableBody({ data }) {
    return (
      <Table.Body>
        {
          data.map(({ order_id, editable, cancelable, legs, ...data_ }, i) => (
            <React.Fragment key={order_id}>
              {legs.map(({ action, symbol }, j) =>
              (
                <Table.Row key={`orderStatus-${i}-${j}`} className={`${data_.status.toLowerCase()}${editable || cancelable ? " editable" : ""}`}>
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data_.status}</Table.Cell>)}
                  <Table.Cell>{action}</Table.Cell>
                  <Table.Cell>{symbol}</Table.Cell>
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data_.quantity}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data_.filled_quantity}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data_.order_type}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data_.price} style="currency" tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data_.duration}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data_.cancel_time} style="date" tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data_.entered_time} style="date" time tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data_.close_time} style="date" time tag="" /></Table.Cell>)}
                </Table.Row>
              ))
              }
            </React.Fragment>
          ))
        }
      </Table.Body>
    );
  }

  const columns = [
    ['status', 'Status', true],
    ['action', 'Action', true],
    ['ticker', 'Symbol', true],
    ['quantity', 'Quantity', true],
    ['filled_quantity', 'Filled', true],
    ['order_type', 'Type', true],
    ['price', 'Price', true],
    ['duration', 'Duration', true],
    ['cancel_time', 'Cancel Time', true],
    ['entered_time', 'Entered Time', true],
    ['close_time', 'Close Time', true]
  ]

  return (
    <SortedTable tableData={statusData} columns={columns} name="orderStatusTable" celled className="history">
      <TableBody />
    </SortedTable>
  )
}

export default OrderStatusTable;
