import * as React from "react"
import { useEffect } from "react";
import { flattenDeep, unique } from "../utils";
import * as Styles from "./styles"
import { Tooltip } from "./tooltip";

import { checkConditional } from "../components/userInputs";

const isRemainderCell = (cell: any, rowIndex: number, cellIndex: number, numRows: number): boolean => {
  return cell.remainder || (numRows > 1 && (rowIndex === numRows - 1));
}

export const ShareTable =
({
  userInput,
  inputStates,
  setInput,
  setError,
}: {
  userInput: UserInputProperties;
  inputStates: Record<string, InputState>;
  setInput: (name: string, value: string, opts?: SetInputOptions) => void;
  setError: (msg: string) => void;
}) => {

  const [erroneousInputCoordinates, setErroneousInputCoordinates] = React.useState<Array<[number, number]>>();

  if (!userInput) {
    return null;
  }

  const {columns, rows} = userInput;
  const numCols = columns?.length || 0;

  const inputState = inputStates?.[userInput.name]

  // set table data defaults if a corresponding input state changes
  // only recalc if any of default-dependent inputs change
  // need to get deduped list of all dependent inputs from table defaults
  const dependentInputNames = unique(
    flattenDeep(userInput?.rows?.map(row => {
      return row?.cells?.map(cell => {
        return cell?.defaults?.map(defawlt => {
          return defawlt.conditionals.map(conditional => {
            return conditional.args?.[0];
          });
        });
      });
    }))
  );

  const dependentInputValues = dependentInputNames?.map(inputName => {
    return inputStates[inputName]?.value;
  });

  const calculateDefaultValuesOfType = (type: 'past' | 'future') => {
    const values = userInput?.rows?.map((row, rowIndex) => {
      let cellsToUse;
      if (type === 'past') {
        cellsToUse = row?.cells?.slice(0, -1);
      } else if (type === 'future') {
        cellsToUse = row?.cells?.slice(-1);
      }
      return cellsToUse?.map((cell, cellIndex) => {
        let defaults = cell.defaults;
        const matchingDefault = defaults.find(item => {
          return item.conditionals.every(conditional => {
            return checkConditional(conditional, inputStates)
          })
        })
        return matchingDefault ? parseInt(matchingDefault.value) : futureValues?.[rowIndex] || 0;
      }) || [];
    }) || [];
    return values;
  }

  const pastValues = calculateDefaultValuesOfType('past');

  const futureValues = inputState.value ? JSON.parse(inputState.value) : [];

  const safeSetInputTo = (value: number[] | undefined) => {
    setInput(userInput.name, JSON.stringify(value), {dontClearComparisonCase: true});
  }

  const recalculateDefaultValues = () => {
    const defaultFutureValuesInArray = calculateDefaultValuesOfType('future') || [];
    const defaultFutureValues = defaultFutureValuesInArray.flat();
    if (JSON.stringify(defaultFutureValues) !== JSON.stringify(futureValues)) {
      safeSetInputTo(defaultFutureValues);
    }
  }

  useEffect(() => { // when inputState changes, if there's no value yet, recalculate from defaults
    if (!inputState?.value) {
      recalculateDefaultValues();
    }
  }, [inputState])

  useEffect(() => { // when a dependent input changes, recalculate from defaults
    const doDependentInputValuesExist = dependentInputValues?.every(value => !!value)
    if (doDependentInputValuesExist || !dependentInputNames) {
      recalculateDefaultValues();
      setErroneousInputCoordinates([])
    }
  }, [JSON.stringify(dependentInputValues)])

  const addCoordinatesToErroneousInputs = (rowIndex: number, cellIndex: number) => {
    setErroneousInputCoordinates(erroneousInputCoordinates => {
      return (erroneousInputCoordinates?.slice() || []).concat([[rowIndex, cellIndex]]);
    });
    setError('Please fill in a value for all inputs')
  }

  const removeCoordinatesFromErroneousInputs = (rowIndex: number, cellIndex: number) => {
    setErroneousInputCoordinates(erroneousInputCoordinates => {
      return erroneousInputCoordinates?.filter(([rowIdx, cellIdx]) => !(rowIdx === rowIndex && cellIdx === cellIndex));
    })
    setError('');
  }

  const onChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    changedRowIndex: number,
    changedCellIndex: number,
  ) => {

    let newValue: number | '' = parseInt(e.target.value);

    if (Number.isNaN(newValue)) {
      newValue = '';
      addCoordinatesToErroneousInputs(changedRowIndex, changedCellIndex);
    } else {
      removeCoordinatesFromErroneousInputs(changedRowIndex, changedCellIndex);
    }

    if (!userInput || !userInput.rows || !userInput.rows.every(row => row && row.cells)) {
      return null;
    }

    const remainders = (userInput.columns || []).slice(-1).map(col => {
      return {
        runningTotal: 0,
        remainder: 0,
      }
    });

    const newFutureValues = userInput.rows.map((row, rowIndex) => {
      return row.cells?.slice(-1).map((cell, cellIndex) => {
        if (rowIndex === changedRowIndex) {
          remainders[cellIndex].runningTotal += (newValue || 0);
          return newValue;
        } else if (isRemainderCell(cell, rowIndex, cellIndex, userInput.rows.length)) {
          const fromValue = cell.column_total || 100;
          remainders[cellIndex].remainder = fromValue - remainders[cellIndex].runningTotal;
          return remainders[cellIndex].remainder
        } else {
          const value = futureValues[rowIndex];
          remainders[cellIndex].runningTotal += value || 0;
          return value;
        }
      })
    })?.flat();

    let errorMessage = '';
    if (remainders.some(({ remainder }) => remainder < 0)) {
      errorMessage = 'Warning: Input shares exceed 100%. Reduce to run.'
    }

    if (JSON.stringify(newFutureValues) !== JSON.stringify(futureValues)) {
      setInput(userInput.name, JSON.stringify(newFutureValues));
      setError(errorMessage);
      userInput.on_change_actions?.forEach(action => {
        switch (action.type) {
          case 'set_input_to':
            setInput(action.target, action.value, {dontClearComparisonCase: true});
            break;
          default:
            break;
        }
      })
    }
  }

  return (
    <>
      <div className="border-l-2 border-gray-200">
        <div
          className="grid gap-x-4 gap-y-2 grid-cols-3 items-center -ml-[2px]"
          // style={{ gridTemplateColumns: `repeat(${numCols + 1}, minmax(0, 1fr))` }}
        >
          {columns?.some(col => !!col) &&
            <>
              <div></div>
              {columns?.map((colName, colIndex) => {
                return (
                  <React.Fragment key={colIndex}>
                    <div className="text-center font-semibold text-gray-700">{colName}</div>
                    {numCols === 1 && <div></div>} {/* empty space to match box widths if there's only one data column */}
                  </React.Fragment>
                )
              })}
            </>
          }
          {rows?.map((row, rowIndex) => {
            const rowName = userInput?.rows?.[rowIndex]?.label;
            return (
              <React.Fragment key={rowIndex}>
                <div className="pl-3 flex items-center">
                  {rowName}
                  <Tooltip data={row.tooltip}></Tooltip>
                </div>
                {numCols === 1 && <div></div>} {/* empty space to match box widths if there's only one data column */}
                {row.cells?.map((cell, cellIndex) => {
                  const colName = userInput?.columns?.[cellIndex];
                  const isPastCell = numCols > 1 && (cellIndex === 0);
                  let isDisabled = isPastCell || isRemainderCell(cell, rowIndex, cellIndex, rows.length) ? true : false;
                  const isValid = !erroneousInputCoordinates?.some(([rowIdx, cellIdx]) => rowIdx === rowIndex && cellIdx === cellIndex);
                  return (
                    <div key={cellIndex}>
                      <Styles.Input
                        className={`block text-right ${!isValid ? '!border-red-600 !border-2' : ''}`}
                        value={isPastCell ? pastValues?.[rowIndex]?.[cellIndex]: futureValues[rowIndex]}
                        type="number"
                        id={`user-inputs--${userInput?.name}-${rowName?.toLowerCase()}${colName ? '-' + colName.toLowerCase() : ''}`}
                        disabled={isDisabled}
                        min={0}
                        max={100}
                        onChange={(e) => onChange(e, rowIndex, cellIndex)}
                        onPaste={(e) => onChange(e, rowIndex, cellIndex)}
                      />
                    </div>
                  )
                })}
              </React.Fragment>
            )
          })}
        </div>
      </div>
    </>

  )
}