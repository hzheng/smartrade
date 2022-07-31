import React, { cloneElement, useEffect, useReducer } from 'react';

import _ from 'lodash';

import { Table } from 'semantic-ui-react';

function SortedTable({ tableData, columns, name, children, ...tableProps }) {
  const [tableState, dispatch] = useReducer(reducer, {
    data: tableData,
    column: null,
    direction: null,
  })
  const { data, column, direction } = tableState;

  function reducer(state, action) {
    switch (action.type) {
      case 'SORT_BY_FIELD':
        if (!action.firstTime && state.column === action.column) {
          return {
            ...state,
            data: state.data.slice().reverse(),
            direction:
              state.direction === 'ascending' ? 'descending' : 'ascending',
          }
        }
        return {
          column: action.column,
          data: _.orderBy(state.data, [action.column]),
          direction: 'ascending',
        }
      default:
        throw new Error();
    }
  }

  function sortByColumn(col, firstTime) {
    dispatch({ type: 'SORT_BY_FIELD', column: col, firstTime });
  }

  useEffect(() => {
    tableState.data = tableData;
    const firstSortCol = columns.find(col => col[2])[0];
    sortByColumn(firstSortCol, true);
  }, [tableData]);

  return (
    <Table sortable {...tableProps}>
      <Table.Header>
        <Table.Row>
          {
            columns.map(([col, title, sortable], index) =>
              sortable ?
                (<Table.HeaderCell key={`${name}${index}`} sorted={column === col ? direction : null}
                  onClick={() => sortByColumn(col)} >{title}</Table.HeaderCell>)
                : (<Table.HeaderCell key={`${name}${index}`}>{title}</Table.HeaderCell>)
            )
          }
        </Table.Row>
      </Table.Header>
      {cloneElement(children, { data })}
    </Table>
  )
}

export default SortedTable;
