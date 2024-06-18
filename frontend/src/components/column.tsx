import * as React from "react"
import { ModuleStateContext, ModuleDispatchContext } from "./comparableResultsModule"
import { triggerResize } from "../utils"
import * as Styles from "./styles"
import { capitalize } from "../utils"
import { trigger } from "../utils/events"
import { Tooltip } from "./tooltip"
import { useEffect } from "react"
import { ColumnChooser } from "./columnChooser"
import { fontSize } from "../utils/constants"
import { useEventListener } from "../hooks/useEventListener"
import { LinkIcon, XIcon } from "@heroicons/react/solid"
import { useAtomValue } from "jotai"
import { isFocusLinkingDisabledAtom } from "../store/store"

// const ClosableButton: React.FC<{}> = ({children}) => {
//   return (
//     <div className="inline-flex">
//       <Styles.Button
//         color="dark-gray"
//         size="small"
//         className="!rounded-r-none"
//       >
//         {children}
//       </Styles.Button>
//       <Styles.Button
//         color="medium-gray"
//         size="small"
//         className="!rounded-l-none"
//       >
//         <XIcon className="w-4 h-4" />
//       </Styles.Button>
//     </div>
//   )
// }

interface ColumnProps {
  title?: string;
  className?: string;
  tabIndex?: number;
  isRunButtonDisabled?: boolean;
  handleRun?: () => Promise<void>;
  isLoading?: boolean;
  isSaveButtonDisabled?: boolean;
  handleSave?: () => Promise<void>;
  hideRibbon?: boolean;
  type: 'inputs' | 'results';
  showColumnDisplayButtons?: boolean;
  constrainWidth?: boolean;
  comparisonResultId?: number | null;
  comparisonIndex?: number;
  ribbonContent?: JSX.Element;
}

const DuplicateCaseButton = ({
  comparisonIndex,
  dispatch,
  isDisabled,
}: {
  comparisonIndex: number;
  dispatch: React.Dispatch<ModuleActionProps>;
  isDisabled: boolean;
}) => {
  return (
    // !isDisabled
    // ?
      <Styles.Button
        className={`ml-3`}
        disabled={isDisabled}
        color="gray"
        id={`duplicate-case-${comparisonIndex}`}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          trigger('duplicateCase', {comparisonIndex: comparisonIndex})}// dispatch({type: 'duplicateComparisonCaseAtIndex', index: comparisonIndex})}
        }
        size="small"
        title="Duplicate inputs"
        // disabled={}
      >
        <svg onClick={(e) => { if (isDisabled) e.stopPropagation(); }} xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
          <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
        </svg>
      </Styles.Button>
    // :
    // null
  )
}

// export const Column: React.FC<ColumnProps> = React.memo(({
export const Column: React.FC<ColumnProps> = ({
  children,
  title,
  className,
  tabIndex,
  isRunButtonDisabled,
  handleRun,
  isLoading,
  isSaveButtonDisabled,
  handleSave,
  hideRibbon = false,
  type,
  showColumnDisplayButtons,
  constrainWidth,
  comparisonResultId,
  comparisonIndex,
  ribbonContent,
}) => {
  const [isOpen, setIsOpen] = React.useState(true);
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const { isComparisonMode, comparisonCases, maxComparisonCases, allowChartTiling, numChartCols, allowComparisons, allowCaseDuplication, showRunAllButton, isAnyColumnFullscreened, isFocusLinkActive } = React.useContext(ModuleStateContext);
  const dispatch = React.useContext(ModuleDispatchContext);

  const isFocusLinkingDisabled = useAtomValue(isFocusLinkingDisabledAtom)

  const afterRunCase = () => {
    const doesAnyCaseHaveFocusModeActive = comparisonCases?.some(comparisonCase => comparisonCase.isFocusModeActive)
    if (type === 'inputs' && isComparisonMode && !doesAnyCaseHaveFocusModeActive) {
      if (isOpen) {
        setIsOpen(false);
      }
    }
    if (type === 'results' && isComparisonMode) {
      if (!isOpen) {
        setIsOpen(true);
      }
    }
  }

  useEventListener('afterRunCase', afterRunCase);

  // const renderCount = React.useRef(0);

  const openColumn = (e) => {
    const eventColumnType = e.detail.type;
    if (eventColumnType === type) {
      setIsOpen(true);
    }
  }

  React.useEffect(() => {
    document.addEventListener('openColumn', openColumn);
    return () => {
      document.removeEventListener('openColumn', openColumn);
    }
  })

  // don't allow collapsed inputs in single-case view
  React.useEffect(() => {
    if (comparisonCases?.length === 1 && type === 'inputs') {
      setIsOpen(true);
    }
  }, [comparisonCases])

  const toggleVisibility = (e) => {
    const isOpening = !isOpen;
    if (isOpening) {
      triggerResize();
    }
    setIsOpen(isOpening);
  }

  const toggleVisibilityIfCollapsed = () => {
    if (!isOpen) {
      toggleVisibility();
    }
  }

  const toggleVisibilityIfComparisonMode = (e) => {
    if (isComparisonMode) {
      toggleVisibility(e);
    }
  }

  const toggleFullscreen = () => {
    dispatch({type: 'setColumnFullscreen', value: !isFullscreen});
    setIsFullscreen(!isFullscreen);
    triggerResize();
  }

  useEffect(() => {
    if (!isAnyColumnFullscreened) {
      setIsFullscreen(false);
    }
  }, [isAnyColumnFullscreened])

  const CollapseArrow = () => {
    return (
      <span onClick={toggleVisibility} className={`inline-block mr-2 h-6 w-6 text-purple-800 cursor-pointer`}>
        {isOpen ?
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          :
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        }
      </span>
    )

  }

  const CollapseButton = () => {
    return (
      <>
        {!isFullscreen &&
          <div onClick={toggleVisibility} className={`transform rotate-90 ${!isComparisonMode ? 'lg:rotate-0' : ''} ${!isComparisonMode && !isOpen ? '-ml-2' : ''} flex text-gray-500 right-2 p-2 w-10 h-10 justify-center items-center cursor-pointer hover:bg-gray-100 rounded`}>
            {isOpen ?
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 border-l-2 border-gray-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              : 
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 border-l-2 border-gray-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            }
          </div>
        }
      </>
    )
  }

  const SaveButton = ({
    comparisonIndex,
    isDisabled,
  }: {
    comparisonIndex: number;
    isDisabled: boolean;
  }) => {

    const isAnalysisResultUnsaved = comparisonCases?.[comparisonIndex]?.isUnsaved;
    const comparisonCaseId = comparisonCases?.[comparisonIndex]?.id;
    const isDisplayingSavedCaseData = comparisonCaseId && !isAnalysisResultUnsaved;

    const button = (
      <Styles.Button
        className="ml-3 w-16 justify-center"
        // color="green"
        id={`save-${comparisonIndex}`}
        disabled={handleSave ? isSaveButtonDisabled : isDisabled}
        onClick={handleSave ? handleSave : (e) => {
          e.preventDefault();
          e.stopPropagation();
          trigger('saveAnalysisResult', {comparisonIndex: comparisonIndex})
        }}
        size="small"
      >
        {isAnalysisResultUnsaved ? 'Save' : 'Saved'}
      </Styles.Button>
    )

    let tooltipMessage;

    if (isDisplayingSavedCaseData) {
      tooltipMessage = 'Case already saved. To save new case, change inputs, run, and save.';
    }
    else if (isDisabled || isSaveButtonDisabled) {
      tooltipMessage = 'Please run before saving';
    } 

    return (
      <>
        {tooltipMessage
          ?
          <Tooltip data={{content: tooltipMessage}}>
            {button}
          </Tooltip>
          :
          button
        }
      </>
    )
  }

  const RunAllButton = ({comparisonIndex}: {comparisonIndex?: number}) => {
    
    const isRunAllButtonDisabled = comparisonCases?.every(c => c.data?.analysisResult)

    const button = 
    <Styles.RunButton
      disabled={isRunAllButtonDisabled}
      // disabled={isRunButtonDisabled || areCaseResultsDisplayed || (comparisonCases && comparisonCases[comparisonIndex].id === 'unsaved')}
      onClick={handleRun ? handleRun : ((e) => {
        e.preventDefault();
        e.stopPropagation();
        trigger('attemptToRunAllCases', null);
      })}
      label="Run All"
      // className={"!ml-auto w-20"}
      className={"w-20"}
      id={`run-all`}
      loading={comparisonCases?.some(comparisonCase => comparisonCase.isRunning)}
    />
    
    // const isLastCase = comparisonCases && comparisonIndex === comparisonCases.length - 1;

    return (
      <>
        {/* {areCaseResultsDisplayed */}
        {showRunAllButton && comparisonCases && comparisonCases.length > 1 &&
          button
        }
          {/* ? */}
          {/* <Tooltip data={{content: 'Case already run. To run new case, change inputs and run.'}}> */}
          {/* </Tooltip> */}
          {/* : */}
          {/* button */}
        {/* } */}
      </>
    )
  }

  const RunButton = ({comparisonIndex}: {comparisonIndex?: number}) => {
    const areCaseResultsDisplayed = !!comparisonCases?.[comparisonIndex]?.data?.analysisResult;
    const button = 
      <Styles.RunButton
        disabled={isRunButtonDisabled || areCaseResultsDisplayed || (comparisonCases && comparisonCases[comparisonIndex].id === 'unsaved')}
        onClick={handleRun ? handleRun : ((e) => {
          e.preventDefault();
          e.stopPropagation();
          trigger('runCase', { comparisonIndex: comparisonIndex });
        })}
        id={`run-${comparisonIndex}`}
        loading={comparisonCases && comparisonCases[comparisonIndex].isRunning}
      />
    
      return (
        <>
          {areCaseResultsDisplayed
            ?
            <Tooltip data={{content: 'Case already run. To run new case, change inputs and run.'}}>
              {button}
            </Tooltip>
            :
            button
          }
        </>
      )
  }

  const FullscreenButton = () => {
    return (
      <>
        {(isOpen || isComparisonMode) &&
          <Styles.Button color="gray" onClick={toggleFullscreen} className="!w-9 !px-0 text-center flex justify-center ml-3">
            {isFullscreen ? 
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              :
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            }
          </Styles.Button>
        }
      </>
    )
  }

  const RibbonTitle = () => {
    return (
      <div
        className={`leading-5 mr-2 flex items-center font-bold text-gray-700 ${!isOpen && !isComparisonMode ? 'lg:writing-mode-vertical lg:absolute lg:top-16 lg:left-5 whitespace-nowrap' : ''}`}
      >
        {isComparisonMode &&
          <CollapseArrow />
        }
        
        {/* {type === 'inputs' && 'Inputs'} */}
        {title ? title : capitalize(type)}
      </div>
    )
  }

  const handleChartColChooserClick = (newNumCols: number) => {
    dispatch({type: 'setNumChartCols', value: newNumCols});
    triggerResize();
  }

  const FocusModeToggle = ({comparisonIndex}: {comparisonIndex: number}) => {

    let tooltip = '';

    let shouldDisplay = false;
    if (isFocusLinkActive) {
      shouldDisplay = comparisonCases?.every(({focusedInputs}) => focusedInputs && focusedInputs.length > 0) ?? false
    } else {
      const focusedInputs = comparisonCases?.[comparisonIndex]?.focusedInputs
      shouldDisplay = (focusedInputs && focusedInputs.length > 0) ?? false
    }

    const isFocusModeActiveForCase = comparisonCases?.[comparisonIndex]?.isFocusModeActive

    if (!isFocusModeActiveForCase) {
      if (shouldDisplay) {
        tooltip = 'Focus on selected inputs, and hide unselected inputs.'
      } else {
        tooltip = 'Select inputs for focusing by clicking the circle to the left of any input'
      } 
    } else {
      tooltip = 'Click to see hidden inputs'
    }

    // if (!shouldDisplay) {
    //   return null;
    // }

    const isFocusLinkButtonEnabled = !isFocusLinkingDisabled
    const isFocusLinkButtonVisible = true
    // const isFocusLinkButtonVisible = comparisonCases && comparisonCases.length > 1

    return (
      <div className="inline-flex items-center">
        <Styles.Button
          size="small"
          className={`flex justify-center !rounded-r-none`}
          color="dark-gray"
          disabled={!shouldDisplay}
          // disabled={!isFocusModeActive && focusedInputs?.length === 0}
          onClick={(e) => {
            e.stopPropagation();
            dispatch({type: 'toggleFocusModeAtIndex', index: comparisonIndex, options: { isFocusLinkingDisabled }});
          }}
          title={tooltip}
        >
          {isFocusModeActiveForCase ? 'Unfocus' : 'Focus'}
        </Styles.Button>
        
        <Styles.Button
          size="small"
          className={`${isFocusLinkButtonVisible ? '!rounded-none' : '!rounded-l-none'} !px-0 !w-8 justify-center`}
          color="medium-gray"
          title="Clear selection of inputs to focus"
          onClick={(e) => {
            e.stopPropagation();
            dispatch({type: 'setFocusedInputsAtIndex', value: [], index: comparisonIndex})
          }}
        >
          <XIcon className="w-4 h-4" />
        </Styles.Button>
        
        {isFocusLinkButtonVisible &&
          <Styles.Button
            size="small"
            className={`!rounded-l-none !px-0 !w-8 justify-center`}
            // color={'gray'}
            disabled={!isFocusLinkButtonEnabled}
            color={`${isFocusLinkActive ? 'green' : 'gray'}`}
            title={isFocusLinkActive ? 
              `Focus applies across all cases. Click to allow focus of inputs only in the case below.`
              :
              (isFocusLinkButtonEnabled
                ?
                `Focus applies only in the case below. Click to allow focus of inputs across all cases.`
                :
                `Can't focus inputs across cases that have different paths`
              )
            }
            onClick={(e) => {
              e.stopPropagation();
              dispatch({type: 'toggleIsFocusLinkActiveWithIndex', index: comparisonIndex})
            }}
          >
            <LinkIcon onClick={(e) => {
              // prevent clicking on icon from collapsing/expanding input accordion if focus link button is disabled
              if (!isFocusLinkButtonEnabled) {
                e.stopPropagation()
              }
            }} className="w-4 h-4" />
          </Styles.Button>
        }
        
      </div>
      
    )

  }

  const Ribbon = ({index}: {index?: number}) => {

    return (
      <div
        style={{top: isComparisonMode ? 3 * fontSize - 1 : 0, height: (3 * fontSize + 1) + 'px' }}
        onClick={(e) => {
          // console.dir(e.target);
          // if (e.target === this) {
          toggleVisibilityIfComparisonMode(e);
          // }
        }}
        id={`accordion--${type}`}
        className={`${isComparisonMode ? 'cursor-pointer hover:bg-gray-100 sticky z-20 top-12 items-stretch' : 'relative gutter-x items-center'} bg-gray-50 border-b border-gray-300 h-12 flex flex-shrink-0 leading-6 shadow-sm ribbon ${isOpen ? 'accordion-open' : 'accordion-closed'}`}
      >
        <div className={`flex text-gray-900 text-lg font-medium ${isComparisonMode ? 'comparison-sidebar' : ''}`}>
          <RibbonTitle />
        </div>
        <div
          className={`${isComparisonMode ? 'comparison-main' : 'ml-auto flex items-center'}`}
          style={{gridTemplateColumns: `repeat(${comparisonCases?.length || 1}, minmax(0, 1fr))`}}
        >
          {type === 'inputs' && !isComparisonMode && comparisonCases?.length && <FocusModeToggle comparisonIndex={0} /> }
          {type === 'inputs' &&
            comparisonCases?.map((comparisonCase, index) => {
              return (
                <div key={[index, comparisonCase.id].join('_')} className="flex items-center">
                  {type === 'inputs' && isComparisonMode && <FocusModeToggle comparisonIndex={index} /> }
                  {(isOpen || (!isOpen && isComparisonMode)) &&
                    <div className="ml-auto flex items-center">

                      {comparisonCase.data?.analysisResult
                        ?
                        <SaveButton comparisonIndex={index} isDisabled={!comparisonCase?.data?.analysisResult || !comparisonCase?.isUnsaved} />
                        :
                        <RunButton comparisonIndex={index} />
                      }

                      {/* <RunButton comparisonIndex={index} /> */}
                      {/*(allowComparisons || handleSave) &&
                         <SaveButton comparisonIndex={index} isDisabled={!comparisonCase?.data?.analysisResult || !comparisonCase?.isUnsaved} />
                      */}
                      {allowCaseDuplication &&
                        <DuplicateCaseButton comparisonIndex={index} dispatch={dispatch} isDisabled={comparisonCases.length >= maxComparisonCases} />
                      }
                      <RunAllButton comparisonIndex={index} />
                    </div>
                  }
                </div>
              )
            })
          }
          {!comparisonCases && handleSave &&
            <SaveButton />
          }
          {!comparisonCases && handleRun &&
            <RunButton />
          }
          {type === 'results' &&
          <>
            <div>
              {ribbonContent}
            </div>
            </>
          }
        </div>
        <div className={`${type === 'results' ? 'ml-auto' : ''} flex flex-row items-center`}>
          {type === 'results' && allowChartTiling && !isComparisonMode && isOpen &&
            <ColumnChooser numCols={numChartCols || 1} setNumCols={handleChartColChooserClick} />
          }
          {!isComparisonMode && type === 'results' &&
            <>
              <FullscreenButton />
              {/* <CollapseButton /> */}
            </>
          }
        </div>
      </div>
    )
  }

  // React.useEffect(() => {

  //   if (children[1] && children[1].savedCaseId !== undefined) {
  //     setIsLoading(false)
  //   }
  //   if (children[1] && moduleState?.comparisonResultIds[0] !== null && comparisonResultIds[0] !== children[1].savedCaseId) {
  //     setIsLoading(true)
  //   } else {
  //     setIsLoading(false)
  //   }
  // })

  const LoadingMessage = ({text}: {text?: string}) => {

    const [hasBeenRunningSuperlong, setHasBeenRunningSuperlong] = React.useState(false)

    React.useEffect(() => {
      const timeout = setTimeout(() => {
        setHasBeenRunningSuperlong(true)
      }, 5000)

      return () => {
        clearTimeout(timeout)
      }
    })

    return (
      <div className="text-center mt-8">
        {text &&
          <span className="inline-block text-gray-400 font-bold text-lg mr-3">{text}</span>
        }
        <svg className="inline-block animate-spin mx-auto h-10 w-10 text-gray-800" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {hasBeenRunningSuperlong &&
          <div className="fade-in text-gray-400 font-bold mt-6">Some analyses may take up to 20 seconds to complete</div>
        }
      </div>
    )
  }

  return (
    <>
      {isComparisonMode ?
        <div
          tabIndex={tabIndex ? tabIndex : undefined}
          onClick={toggleVisibilityIfCollapsed}
          id={type}
          className={`
            flex flex-col relative bg-white
            ${type === 'results' ? 'flex-auto' : ''}
            ${isOpen ? 'border-b border-gray-300' : ''}
            ${isFullscreen ? 'w-[calc(100vw - 4rem)] ml-16 h-[calc(100vh - 3rem)] fixed inset-0 z-20 bg-white border-l' : ''}
            ${constrainWidth && !isFullscreen && isOpen ? 'lg:flex-initial lg:w-[400px] lg:max-w-1/2' : ''}
            ${className ? className : ''}
          `}
          
        >
          {/* <div className="py-1 px-2 bg-red-500 text-white">Column rendered {(renderCount.current ++)} time(s)</div> */}

          <Ribbon />
          <div className={`column-content ${isOpen ? 'flex flex-col h-full' : 'hidden'}`}>
            <div>
              {children}
            </div>
          </div> 
        </div>
      :
        <div
          tabIndex={tabIndex ? tabIndex : undefined}
          onClick={toggleVisibilityIfCollapsed}
          id={type}
          className={`
            flex flex-col relative bg-white 
            ${type === 'inputs' ? 'lg:border-r border-gray-300' : ''}
            ${isOpen ? 'border-b border-gray-300' : ''}
            ${type === 'results' && !isOpen ? 'border-r border-gray-300' : ''}
            ${isOpen ? 
              `lg:flex-1`
              :
              'h-16 lg:h-auto lg:w-16 cursor-pointer hover:bg-gray-50'
            }
            ${isFullscreen ? 'w-[calc(100vw - 4rem)] ml-16 h-[calc(100vh - 3rem)] fixed inset-0 top-12 z-20 bg-white border-l' : 'overflow-x-hidden overflow-y-auto'}
            ${constrainWidth && !isFullscreen && isOpen ? 'lg:flex-initial lg:w-[400px] lg:max-w-1/2' : ''}
            ${className ? className : ''}
          `}
        >
          {/* <div className="py-1 px-2 bg-red-500 text-white">Rendered {(renderCount.current ++)} time(s)</div> */}
          {!hideRibbon &&
            <>
              {type === 'inputs' &&
                <Ribbon />
              }
              {type === 'results' &&
                <>
                  {/* {allowComparisons && */}
                    <Ribbon />
                  {/* } */}
                </>
              }
            </>
          }
          <div id={type === 'results' ? 'non-comparison-results-scroll-wrapper' : ''} className={`${isOpen ? `flex flex-col h-full ${type === 'results' ? 'overflow-y-scroll' : 'overflow-y-auto'}` : 'hidden'}`}>
            <div className={type === 'inputs' ? 'py-2' : ''}>
              {type === 'results' && comparisonCases?.[0].isRunning ? 
                <LoadingMessage />
                :
                children
              }
            </div>
          </div> 
        </div>
      }
    </>
  )

}
