import * as React from "react"
import { triggerResize } from "../utils"

const columnOptions = [
  {
    numCols: 1,
    path: <rect fill="transparent" strokeWidth="2" stroke="currentColor" x="2" y="2" width="20" height="20" rx="3" id="svg_1"/>
  },
  {
    numCols: 2,
    path: <>
      <rect fill="transparent" strokeWidth="2" stroke="currentColor" x="2" y="2" width="20" height="20" rx="1" id="svg_1"/>
      <line fill="none" stroke="currentColor" strokeWidth="2" rx="15" x1="12" y1="2" x2="12" y2="22" id="svg_2" strokeLinejoin="round" strokeLinecap="round"/>
    </>
  },
  {
    numCols: 3,
    path: <>
      <rect fill="transparent" strokeWidth="2" stroke="currentColor" x="2" y="2" width="20" height="20" rx="1" id="svg_1"/>
      <line fill="none" stroke="currentColor" strokeWidth="2" rx="15" x1="8.5" y1="2" x2="8.5" y2="22" id="svg_2" strokeLinejoin="round" strokeLinecap="round"/>
      <line fill="none" stroke="currentColor" strokeWidth="2" rx="15" x1="15.5" y1="2" x2="15.5" y2="22" id="svg_2" strokeLinejoin="round" strokeLinecap="round"/>
    </>
  }
]

export const ColumnChooser = ({
  className,
  numCols,
  setNumCols,
}: {
  className?: string;
  numCols: number;
  setNumCols: (newNumCols: number) => void;
}) => {
  return (
    <div className={`bg-gray-200 h-9 pl-2 py-2 rounded border border-gray-300 inline-flex items-center ml-auto ${className ? className : ''}`}>
      {columnOptions.map((option, index) => {
        return (
          <svg
            key={index}
            className={`mr-2 cursor-pointer h-5 w-5 rounded transition-colors font-semibold ${option.numCols === numCols ? ' text-gray-600' : 'text-gray-400 hover:text-gray-400'}`}
            viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
            onClick={() => {
              setNumCols(option.numCols);
              setTimeout(() => {triggerResize()}, 10);
            }}
          >
            {option.path}
          </svg>
        )
      })}
    </div>
  )
}