import React, { useCallback, useEffect, useMemo, useState } from "react";
import * as Styles from "./styles"

const redColor = "rgba(255, 0, 0, 0.2)";
const greenColor = "rgba(0, 128, 0, 0.4)";

export type Cell = {
  column: string;
  row: string;
  value: number;
  editable: boolean;
  min?: number;
  max?: number;
  computed?: (table: Table) => number;
};

export const cellKey = (column: string, row: string): string => {
  return `column-${column},row-${row}`;
};

export type Table = {
  columns: string[];
  rows: string[];
  cells: Record<string, Cell>;
  getCell: (column: string, row: string) => Cell;
  setCells: React.Dispatch<React.SetStateAction<Record<string, Cell>>>;
  createCellIndex: (
    acc: Record<string, Cell>,
    cell: Cell
  ) => {
    [x: string]: Cell;
  };
  setCellValue: (cell: Cell, value: number) => void;
  getCellValue: (cell: Cell) => number;
};

export const useTable = ({
  columns,
  rows,
}: {
  columns: string[];
  rows: string[];
}): Table => {
  const initial: Record<string, Cell> = {};
  const [cells, setCells] = useState(initial);

  const createCellIndex = useCallback(
    (acc: Record<string, Cell>, cell: Cell) => ({
      ...acc,
      [cellKey(cell.column, cell.row)]: cell,
    }),
    []
  );

  // initialize empty table
  useEffect(() => {
    const emptyCells: Cell[] = [];

    columns.forEach((column) => {
      rows.forEach((row) => {
        const cell: Cell = {
          column,
          row,
          editable: true,
          value: 0,
        };

        emptyCells.push(cell);
      });
    });

    // setCells(() => emptyCells.reduce(createCellIndex, {}));
  }, []);

  const setCellValue = useCallback(
    (cell: Cell, value: number) => {
      setCells({
        ...cells,
        [cellKey(cell.column, cell.row)]: { ...cell, value },
      });
    },
    [cells, setCells]
  );

  const getCell = useCallback(
    (column: string, row: string) => {
      return cells[cellKey(column, row)];
    },
    [cells]
  );

  const getCellValue = useCallback(
    (cell: Cell): number => {
      if (cell.computed) {
        return cell.computed(table);
      } else {
        return cell.value;
      }
    },
    [cells]
  );

  const table = {
    columns,
    rows,
    cells,
    setCells,
    createCellIndex,
    setCellValue,
    getCell,
    getCellValue,
  };

  return table;
};

export const TableInputs = ({
  table,
  cellValueChanged,
}: {
  table: Table;
  cellValueChanged?: (cell: Cell, value: number) => void;
}): JSX.Element => {
  return (
    <table className="table-fixed w-full">
      <thead>
        <tr>
          <th
            className="text-sm"
            style={{ width: "20%", fontWeight: "normal" }}
          ></th>
          {table.columns.map((column, i) => {
            return (
              <th
                key={i}
                className="text-sm"
                style={{ width: "40%", fontWeight: "normal" }}
              >
                {column}
              </th>
            );
          })}
        </tr>
        {table.rows.map((row, y) => {
          return (
            <tr key={y} className="font-medium text-gray-700">
              <td key="row" style={{ width: "20%" }}>
                {row}
              </td>
              {table.columns.map((column, x) => {
                const cell = table.cells[cellKey(column, row)];
                const value = cell ? table.getCellValue(cell) : 0;

                return (
                  <td key={x} style={{ width: "40%" }} className={x === 0 ? 'pr-1' : 'pl-1'}>
                    <Styles.Input
                      className="mt-1 block w-full border border-gray-400"
                      type="number"
                      value={value}
                      disabled={!cell?.editable}
                      min={cell?.min}
                      max={cell?.max}
                      onChange={(e) => {
                        if (cell) {
                          const newValue = parseInt(e.target.value, 10);
                          table.setCellValue(cell, newValue);
                          if (cellValueChanged) {
                            cellValueChanged(cell, newValue);
                          }
                        }
                      }}
                    />
                  </td>
                );
              })}
            </tr>
          );
        })}
      </thead>
    </table>
  );
};
TableInputs.displayName = "TableInputs";
