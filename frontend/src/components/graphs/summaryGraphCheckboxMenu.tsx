import { Menu, Transition } from '@headlessui/react'
import * as React from 'react'
import { Fragment } from 'react'
import { ChevronDownIcon } from '@heroicons/react/solid'
import { ModuleDispatchContext, ModuleStateContext } from '../comparableResultsModule'
import { unique } from '../../utils'

export const SummaryGraphCheckboxMenu = ({
  variables,
  variableIndexesPlotted,
  setVariableIndexesPlotted,
}: {
  variables: string[];
  variableIndexesPlotted: number[];
  setVariableIndexesPlotted: React.Dispatch<React.SetStateAction<number[]>>;
}) => {

  const { type, isComparisonMode } = React.useContext(ModuleStateContext);
  const dispatch = React.useContext(ModuleDispatchContext)
  // const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const buttonRef = React.useRef(null);

  const menuItemClasses = "inline-flex items-center py-1 px-4 cursor-pointer hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900";

  const closeMenu = () => {
    buttonRef?.current?.click();
  }

  // const [variableIndexesPlotted, setVariableIndexesPlotted] = React.useState(defaultVariableIndexesPlotted);

  // console.log(defaultVariableIndexesPlotted.map(varIndex => variables[varIndex]));
  // console.log(variableIndexesPlotted);

  // useEffect(() => {
  //   setCheckedVariables([]);
  // }, [JSON.stringify(savedCases?.map(savedCase => savedCase.id))])

  // useEffect(() => {
  //   console.log('empty useeffect');
  // })

  // useEffect(() => {
  //   console.log('effect');
  // }, [buttonRef.current])

  // const delaySetCheckedVariables = () => {
  //   setTimeout(() => {
  //     setVariableIndexesPlotted([]);
  //   }, 1);
  // }

  const toggleVariableIndexChecked = (index: number) => {
    const isAlreadyChecked = variableIndexesPlotted.some(checkedIndex => checkedIndex === index);
    if (isAlreadyChecked) {
      setVariableIndexesPlotted([...variableIndexesPlotted].filter(checkedIndex => checkedIndex !== index));
    } else {
      setVariableIndexesPlotted(unique([...variableIndexesPlotted].concat(index)));
    }
  }

  return (
    <div className="flex items-center flex-shrink-0 mr-4">
      <div className="text-left">{/*} fixed top-4">*/}
        <Menu as="div" className="relative inline-block text-left">
          {({ open }) => {
            return (
              <>
                <div>
                  <Menu.Button ref={buttonRef} className="inline-flex justify-center w-full px-4 py-1 bg-white font-medium text-gray-700 border border-gray-300 rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">
                    Variables Shown
                    <ChevronDownIcon
                      className="w-5 h-5 ml-2 -mr-1 text-violet-200 hover:text-violet-100"
                      aria-hidden="true"
                    />
                  </Menu.Button>
                </div>
                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-100"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-100"
                >
                  <Menu.Items className="absolute left-0 w-[50rem] mt-1 origin-top-right bg-white divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-2" style={{columnCount: 3, columnGap: '1rem'}}>
                      {variables?.map((variable, index) => {
                        return (
                          <div
                            key={index}
                            className={menuItemClasses}
                            onClick={() => {
                              if (variableIndexesPlotted.length === 0) {
                                // dispatch({type: 'setComparisonCaseIdAtIndex', index: comparisonIndex, value: savedCase.id, dispatch: dispatch })
                                closeMenu();
                              } else {
                                // console.log(savedCase.id);
                                toggleVariableIndexChecked(index);
                                // toggle
                                // setCheckedVariables(unique([...checkedVariables].concat(savedCase.id)));
                              }
                            }}
                          >
                            {/* <div className=""> */}
                              <input
                                type="checkbox"
                                className="rounded border-gray-300 mr-2 h-5 w-5"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleVariableIndexChecked(index);
                                }}
                                onChange={(e) => {}} // to squelch react error msg about not having onchange
                                checked={variableIndexesPlotted.some(checkedIndex => checkedIndex === index)}
                              />
                              <a key={index}>{variable}</a>
                            </div>
                          // </div>
                        )
                      })}
                    </div>

                  </Menu.Items>
                </Transition>
              </>
            )
          }}
        </Menu>
      </div>
    </div>
    
  )
}