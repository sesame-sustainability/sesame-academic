import * as React from "react"
import { ModuleStateContext, ModuleDispatchContext, getCaseNameFromComparisonCaseAtIndex } from "./comparableResultsModule";
import * as Styles from "./styles"
import { getHeaderTitle } from "../utils";
import { SavedItemMenu } from "./savedItemMenu";

const AddCompareColumnButton = () => {

  const dispatch = React.useContext(ModuleDispatchContext);
  const { comparisonCases, maxComparisonCases } = React.useContext(ModuleStateContext);

  return (
    <Styles.Button
      className="ml-auto"
      onClick={() => dispatch({type: 'addComparisonCol'})}
      size="small"
      color="dark-gray"
      disabled={(comparisonCases?.length || 0) >= maxComparisonCases}
      id="add-compare-col"
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
      </svg>
      {comparisonCases?.length === 1 &&
        <span className="ml-2">Compare</span>
      }
    </Styles.Button>
  ) 
}

const CloseCompareColumnButton = ({comparisonIndex}: {comparisonIndex: number}) => {
  
  const dispatch = React.useContext(ModuleDispatchContext);
  
  return (
    <Styles.Button
      className="ml-auto"
      id={`close-case-${comparisonIndex}`}
      color="gray"
      onClick={() => dispatch({type: 'removeComparisonCaseAtIndex', index: comparisonIndex})}
      size="small"
      // disabled={}
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
      </svg>
    </Styles.Button>
  )
}

const EditableTextField = ({text}: {text: string}) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const nameRef = React.useRef<HTMLInputElement>(null);
  // console.log(isEditing)
  return (
    <>
      {isEditing ?
        <form 
          className="flex items-center"
          onSubmit={(e) => {
            e.preventDefault();
            // console.log('submit edit name form');
            const name = nameRef.current?.value;
            // dispatch({type: 'updateSavedCaseName', value: name })
          }}
        >
          <Styles.Input type="text" ref={nameRef} defaultValue={text} />
          <Styles.Button size="small" className="ml-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </Styles.Button>
        </form>
        :
        <>
          <span className="mr-2 text-lg">{text}</span>
          {/* <svg onClick={() => setIsEditing(true)} xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500 cursor-pointer hover:text-gray-900" viewBox="0 0 20 20" fill="currentColor">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg> */}
        </>
      }
    </>
  )
}

export const AppHeader = ({
  isSidebarOpen,
  extraContent,
}: {
  isSidebarOpen: boolean;
  extraContent: JSX.Element;
}) => {

  const { comparisonCases, savedBatch, isComparisonMode, allowComparisons, maxComparisonCases, allowChartTiling, numChartCols, type, headerTitle } = React.useContext(ModuleStateContext) as ModuleStateProps;
  // const dispatch = React.useContext(ModuleDispatchContext)
  const comparisonCaseIds = comparisonCases?.map(comparisonCase => comparisonCase.id);
  const numCases = comparisonCases ? comparisonCases.length : 0

  // const comparisonIndex = (index || 0) - 1; // because the current analysis result takes up the first index
  // const comparisonResultId = comparisonResultIds && comparisonIndex >= 0
  //   ?
  //   comparisonResultIds[comparisonIndex]
  //   :
  //   undefined;
  // console.log('column index:', index);
  // console.log('comparisonResultId', comparisonResultId);

  const title = headerTitle || getHeaderTitle();

  if (!title) return null;

  return (
    <div className="bg-gray-100 border-b border-gray-300 h-12 flex-shrink-0 sticky top-0 z-30">
      <div className={`h-full flex items-center`}>
        <div className={`${isComparisonMode ? 'comparison-sidebar gutter-x' : 'gutter-l'} flex-initial text-lg py-2 leading-5 font-bold text-gray-700 flex !flex-row !items-center flex-nowrap`}>
          <span>{title}</span>
          <div className="!pr-0 !pl-3">{extraContent}</div>
        </div>
        {isComparisonMode ?
          <div className="grid h-full comparison-main flex-auto items-center" style={{gridTemplateColumns: `repeat(${numCases}, minmax(0, 1fr))`}}> 
            {/* <div className="px-2 border-l border-gray-300 h-full flex items-center">
              <SavedCaseMenu />
            </div> */}
            {comparisonCaseIds?.map((comparisonCaseId, index) => {
              const comparisonCase = comparisonCases?.[index];
              const isLastResultColumn = index === (numCases - 1);
              return (
                <div key={index} className={`h-full px-2 flex items-center border-l border-gray-300`}>
                  {/* {comparisonResultId === null ? */}
                      <SavedItemMenu
                        comparisonIndex={index}
                        activeItem={comparisonCase}
                        activeItemId={comparisonCase?.savedCaseId}
                        activeItemName={getCaseNameFromComparisonCaseAtIndex(comparisonCases?.[index], index)}
                        collectionName="savedCases"
                        itemTitle="Case"
                        isUnsaved={comparisonCase?.isUnsaved}
                      />
                      {/* {(index > 0 || (index === 0 && comparisonResultId !== null)) && */}
                        <CloseCompareColumnButton comparisonIndex={index} />
                      {/* } */}
                  {isLastResultColumn && 
                    <>
                      {numCases < maxComparisonCases &&
                        <span className="ml-3">
                          <AddCompareColumnButton />
                        </span>
                      }
                      {/* <span className="ml-4">
                        <MenuButton />
                      </span> */}
                    </>
                  }
                </div>
              )
            })}   
          </div>
        :
          <>
            {allowComparisons && numCases === 1 &&
              <>
                {/* <SavedCaseMenu activeItemId={comparisonCaseIds ? comparisonCaseIds[0] : null} comparisonIndex={0} /> */}
                <SavedItemMenu
                  collectionName="savedCases"
                  itemTitle="Case"
                  comparisonIndex={0}
                  activeItem={comparisonCases?.[0]}
                  activeItemId={comparisonCases?.[0]?.savedCaseId}
                  activeItemName={getCaseNameFromComparisonCaseAtIndex(comparisonCases?.[0], 0)}
                  isUnsaved={comparisonCases?.[0]?.isUnsaved}
                />
                <SavedItemMenu
                  collectionName="savedBatches"
                  itemTitle="Batch"
                  comparisonIndex={0}
                  activeItem={savedBatch}
                  activeItemId={savedBatch?.id}
                  activeItemName={savedBatch?.name}
                />
                <div className="gutter-r ml-auto">
                  <AddCompareColumnButton />
                </div>
                {/* <span className="ml-2 mr-4">
                  <MenuButton />
                </span> */}
              </>
            }
          </>
        }     
      </div>
    </div>
  )
}