import * as React from "react"
import { ModuleStateContext } from "./comparableResultsModule"

interface TiledColumnProps {
  children: React.ReactNodeArray,
  cols?: number,
  className?: string,
  numCols?: number, // this is optional - if not passed, will use module state numChartCols
  showBorders?: boolean; // hides borders between columns and rows
}

export const TiledColumn: React.FC<TiledColumnProps> = ({
  children,
  className,
  numCols,
  showBorders = true,
}) => {

  const {numChartCols, isComparisonMode} = React.useContext(ModuleStateContext);

  // const renderCount = React.useRef(0);
  
  const numColsToUse = numCols || numChartCols || 1;
  const numRows = Math.ceil(children?.length / numColsToUse);

  return (
    <div className={className ? className : ''}>
      {/* <div className="py-1 px-2 bg-red-500 text-white">TiledColumn rendered {(renderCount.current ++)} time(s)</div> */}

      <div
        className={`grid w-full`}
        style={{gridTemplateColumns: `repeat(${numColsToUse || 1}, minmax(0px, 1fr))`}}
      >
        {children.map((child, index) => {
          const isInLastRow = (index + 1) / numColsToUse > (numRows - 1);
          return (
            <div
              key={index}
              style={showBorders ?
                {
                  borderRightWidth: (index + 1) % numColsToUse === 0 ? '' : '1px',
                  borderBottomWidth: isInLastRow ? '' : '1px',
                }
                :
                {}
              }
              className={`${isComparisonMode ? 'h-full border-gray-200' : ''} max-w-full`}
            >
              {child}
            </div>
          )
        })}
      </div>
    </div>
  )
}