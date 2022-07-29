import React, { useContext, useEffect, useState } from 'react';

import { Message, Table } from 'semantic-ui-react';

import AppContext from "./app_context";
import { FormattedField } from './format';

import './order_status_pane.scss';

function OrderStatusTable({ orderData }) {
  return (
    <Table celled structured>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Status</Table.HeaderCell>
          <Table.HeaderCell>Action</Table.HeaderCell>
          <Table.HeaderCell>Symbol</Table.HeaderCell>
          <Table.HeaderCell>Quantity</Table.HeaderCell>
          <Table.HeaderCell>Filled</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Price</Table.HeaderCell>
          <Table.HeaderCell>Duration</Table.HeaderCell>
          <Table.HeaderCell>Cancel Time</Table.HeaderCell>
          <Table.HeaderCell>Entered Time</Table.HeaderCell>
          <Table.HeaderCell>Close Time</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {
          orderData.map(({ order_id, editable, cancelable, legs, ...data }, i) => (
            <React.Fragment key={order_id}>
              {legs.map(({ action, symbol }, j) =>
              (
                <Table.Row key={`orderStatus-${i}-${j}`} className={`${data.status.toLowerCase()}${editable || cancelable ? " editable" : ""}`}>
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data.status}</Table.Cell>)}
                  <Table.Cell>{action}</Table.Cell>
                  <Table.Cell>{symbol}</Table.Cell>
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data.quantity}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data.filled_quantity}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data.order_type}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data.price} style="currency" tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}>{data.duration}</Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data.cancel_time} style="date" tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data.entered_time} style="date" time tag="" /></Table.Cell>)}
                  {(j == 0) && (<Table.Cell rowSpan={legs.length}><FormattedField value={data.close_time} style="date" time tag="" /></Table.Cell>)}
                </Table.Row>
              ))
              }
            </React.Fragment>
          ))
        }
      </Table.Body>
    </Table>
  );
}

function OrderStatusPane() {
  const { account, load } = useContext(AppContext);
  const [orderData, setOrderData] = useState([]);

  useEffect(() => {
    console.log("Rendering OrderStatusPane for account:", account);
    loadOrders();
  }, [account]);

  function loadOrders() {
    const url = `/account/${account}/orders`;
    load(url, data => { setOrderData(data); }, "order status");
  }

  return (
    <div className="OrderStatusPane">
      <Message>Total orders: {orderData.length}</Message>
      { orderData.length > 0 && <OrderStatusTable orderData={orderData} />}
    </div>
  );
}

export default OrderStatusPane;
