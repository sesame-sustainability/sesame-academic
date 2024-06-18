import * as React from "react"
import { Label, Select } from "./styles";
import UserInputs, { checkConditional, InputBlock } from "./userInputs";
import Accordion from "./accordion";
import useUserInputs, { getInputValuesRecordFromInputStates } from "../hooks/useUserInputs";
import { capitalStr, unique } from "../utils";
import useAppMetadata from "../hooks/useAppMetadata";
import { getCaseNameFromComparisonCaseAtIndex, ModuleDispatchContext, ModuleStateContext, useRunCaseAtIndex } from "./comparableResultsModule";
import { useRunAndSaveCaseEventListeners } from "../hooks/useRunAndSaveCaseEventListeners";
import { debounce } from "lodash";
import { Toggle } from "./toggle";
import { useSetting, useSettingValue } from "../hooks/useSettings";
import { getCurrentDataSourceVersions, getCustomInputValues, getDataSourceVersion, getInputValuesByStage } from "./pages/LCATEA";
import { customAlert } from "./customAlert";
import { useMakeSureSomeInputsAreVisibleAtIndex } from "../hooks/useMakeSureSomeInputsAreVisibleAtIndex";
import { useAtom } from "jotai";
import { pathsByCaseIdAtom } from "../store/store";
import { useMount, useUnmount } from "../hooks/useMount";
import { useInvalidateStaleCases } from "../hooks/useInvalidateStaleCases";

const startWithOptions = ['product', 'resource'];

const additionalBackendInputs = [
  {
    name: 'compute_cost',
    label: 'Compute cost',
    type: 'toggle',
    // options: [
    //   { label: 'Yes', value: 'true' },
    //   { label: 'No', value: 'false' }
    // ],
  }
]

export type StageInputValues = {
  nodeChosen: string;
  inputValues: Record<string, string>;
}

export type CustomInputValues = {
  startWith: string;
  selectedProduct: string;
  selectedProductType: string;
  selectedResource: string;
  additionalBackendInputValues: Record<string, boolean>;
  dataSourcesChosen: Array<string | null>;
  dataSourceVersions: Array<number | null>;
}

export type PathwayCreatorState = {
  startWith: string,
  selectedProduct: string,
  selectedProductType: string,
  selectedResource: string,
  filteredProducts: string[],
  filteredProductTypes: string[],
  filteredResources: string[],
  nodesChosen: Array<string | null>,
  dataSourcesChosen: Array<string | null>,
  nodeOptionsAtEachStage: Array<string[] | undefined>,
  farthestAutomaticallyTraversedStageIndex: number,
}

const defaultPathwayCreatorState: PathwayCreatorState = {
  startWith: 'product',
  selectedProduct: '',
  selectedProductType: '',
  selectedResource: '',
  filteredProducts: [],
  filteredProductTypes: [],
  filteredResources: [],
  nodesChosen: [],
  dataSourcesChosen: [],
  nodeOptionsAtEachStage: [],
  farthestAutomaticallyTraversedStageIndex: 0,
}

const openAccordionIfStageHasInvalidInputs = ({
  userInputsAtThisStage,
  stageInputHandler,
  areThereMultipleNodeOptionsAtThisStage,
  setIsOpen,
}: {
  userInputsAtThisStage: UserInputProperties[] | undefined;
  stageInputHandler: InputHandler;
  areThereMultipleNodeOptionsAtThisStage: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  if ((userInputsAtThisStage && userInputsAtThisStage?.length > 0 && Object.keys(stageInputHandler.inputStates)?.length > 0 && !stageInputHandler.isValid) || areThereMultipleNodeOptionsAtThisStage) {
    setIsOpen(true);
  } else {
    // setIsOpen(false)
  }
}

const areStagePropsEqual = (prevProps: StageProps, nextProps: StageProps) => {
  const propsToCompare = ['nodesChosen', 'dataSourcesChosen', 'nodeOptionsAtEachStage', 'stageInputHandler', 'comparisonIndex', 'isOpen', 'focusedInputs'];
  if (typeof prevProps === 'undefined' && typeof nextProps === 'undefined') {
    return true;
  }
  if (!prevProps || !nextProps) {
    return false;
  }
  const areEqual = propsToCompare.every(prop => {
    return JSON.stringify(prevProps[prop as keyof StageProps]) === JSON.stringify(nextProps[prop as keyof StageProps]);
  })
  return areEqual;
}

interface StageProps {
  stage: Stage,
  stages: Stage[],
  index: number,
  nodesChosen: Array<string | null>;
  dataSourcesChosen: Array<string | null>;
  nodeOptionsAtEachStage: Array<string[]>;
  setNodeChosenAtIndex: (nodeChosen: string | null, index: number) => void;
  setDataSourceChosenAtIndex: (dataSourceChosen: string | null, index: number) => void;
  stageInputHandler: InputHandler;
  comparisonIndex: number;
  isOpen: boolean;
  toggleInputGroupOpenState: (name: string) => void;
  focusedInputs: string[];
}

// just render all stages, but if they're done already, set them to display as done
const Stage = React.memo(({
  stage,
  stages,
  index,
  nodesChosen,
  dataSourcesChosen,
  nodeOptionsAtEachStage,
  setNodeChosenAtIndex,
  setDataSourceChosenAtIndex,
  stageInputHandler,
  comparisonIndex,
  isOpen,
  toggleInputGroupOpenState,
  focusedInputs,
}: StageProps) => {

  // this complicated thing handles the automatic opening of accordions that have invalid inputs inside (debounced to avoid jank) - we need one of these debounced functions per stage b/c we have one user inputs handler and accordion isOpen handler per stage
  const debouncedOpenAccordionIfStageHasInvalidInputs = React.useRef({
    func: debounce(openAccordionIfStageHasInvalidInputs, 1000, {leading: false, trailing: true})
  });

  const { comparisonCases } = React.useContext(ModuleStateContext)
  const comparisonCase = comparisonCases?.[comparisonIndex]
  const isFocusModeActive = comparisonCase?.isFocusModeActive

  const dispatch = React.useContext(ModuleDispatchContext);

  const activityAtThisStage = stage.activities?.find(activity => { return activity.id.indexOf(nodesChosen[index] as string) > -1 })
  const dataSourceAtThisStage = dataSourcesChosen[index];
  const userInputsAtThisStage = (
    dataSourceAtThisStage
    ?
    activityAtThisStage?.sources?.find(source => source.id === dataSourceAtThisStage)?.user_inputs
    :
    activityAtThisStage?.sources[0]?.user_inputs
  );
  const areThereMultipleNodeOptionsAtThisStage = nodeOptionsAtEachStage[index]?.length > 1;
  const hasNodeBeenChosenAtThisStage = nodesChosen[index];
  let shouldDisplayThisStage = (
    areThereMultipleNodeOptionsAtThisStage
    ||
    (hasNodeBeenChosenAtThisStage && userInputsAtThisStage && userInputsAtThisStage.length > 0)
  );

  // if (isFocusModeActive) {
  //   // check if any inputs are focused - if not, don't display this stage
  //   let areAnyVisibleInputs = false;
  //   const checkIsInputFocused = (userInput: UserInputProperties) => {
  //     // only do this check for inputs that are visible (i.e. their conditionals check out)
  //     if ((userInput?.conditionals as Conditional[])?.every(conditional => checkConditional(conditional, stageInputHandler.inputStates))) {
  //       if (focusedInputs?.includes(userInput.name)) {
  //         areAnyVisibleInputs = true;
  //       }
  //     }
  //   }
  //   userInputsAtThisStage?.map(userInput => {
  //     if (userInput.type === 'group') {
  //       userInput.children.map(userInput => {
  //         checkIsInputFocused(userInput)
  //       })
  //     } else {
  //       checkIsInputFocused(userInput)
  //     }
  //   })
  //   if (!areAnyVisibleInputs) {
  //     shouldDisplayThisStage = false;
  //   }
  // }

  React.useEffect(() => {
    // setIsOpen(false);
    debouncedOpenAccordionIfStageHasInvalidInputs.current.func({
      userInputsAtThisStage,
      stageInputHandler,
      areThereMultipleNodeOptionsAtThisStage,
      setIsOpen: () => toggleInputGroupOpenState(stage.name || ''),
    })
  }, [stageInputHandler.isValid, stageInputHandler.inputStates, areThereMultipleNodeOptionsAtThisStage])

  // this is used for fetching input data from backend I think?
  // const currentSourceId = activityAtThisStage?.sources[0]?.id;
  const availableSourcesAtThisStage = activityAtThisStage?.sources;
  const nodeOptionsAtThisStage = nodeOptionsAtEachStage[index];
  const nodeChosenAtThisStage = nodesChosen[index];
  const stageName = stage.name?.length === 3 ? stage.name : stage.name?.split(/(?=[A-Z])/).join(' ') || ''; // hack so that TEA doesn't get spaces between it

  const stageContent = (
    <div>
      {areThereMultipleNodeOptionsAtThisStage &&
        <>
          <InputBlock>
            <Label className="col-span-2">{stageName} type</Label>
            <Select value={nodeChosenAtThisStage || ''} onChange={(e) => { setNodeChosenAtIndex(e.target.value, index) }}>
              <option disabled={true} selected={true} label={"Choose one"} />
              {nodeOptionsAtThisStage.map(nodeOption => {
                const nodeLabel = stages[index]?.activities?.find(activity => activity.id === nodeOption)?.name;
                return (
                  <option value={nodeOption} label={nodeLabel}></option>
                )
              }
              )}
            </Select>
          </InputBlock>
          {/* <hr className="my-4" /> */}
        </>
      }
      {availableSourcesAtThisStage && availableSourcesAtThisStage.length > 1 && !isFocusModeActive &&
        <InputBlock className="mb-0">
          <Label className="col-span-2">Data Source</Label>
          <Select
            value={dataSourcesChosen[index]}
            id="user-inputs--select-data-source"
            onChange={(e) => {
              const newDataSource = e.target.value;
              dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
              setDataSourceChosenAtIndex(newDataSource, index);
            }}
          >
            {availableSourcesAtThisStage.map(source => (
              <option value={source.id} label={source.name}>{source.name}</option>
            ))}
          </Select>
        </InputBlock>
      }
      {userInputsAtThisStage &&
        <UserInputs
          userInputs={userInputsAtThisStage}
          inputStates={stageInputHandler.inputStates}
          comparisonIndex={comparisonIndex}
          setInput={(name, value, opts) => {
            dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
            stageInputHandler.setInput(name, value, opts);
          }}
          setInputError={stageInputHandler.setInputError}
        />
      }
    </div>
  )

  if (!shouldDisplayThisStage) {
    return null;
  }

  const areAnyFocusedInputs = Object.keys(stageInputHandler.inputStates ?? {}).some(inputName => {
    return focusedInputs?.includes(inputName)
  })

  return (
    <>
      {isFocusModeActive
        ?
        stageContent
        :
        <Accordion
          title={stageName}
          // isOpen={inputGroupOpenStates?.[stageName]}
          // setIsOpen={(e) => {
          //   dispatch({type: 'toggleInputGroupOpenStateAtComparisonIndex', value: stageName, index: comparisonIndex})
          // }}
          isOpen={isOpen}
          setIsOpen={(e) => {
            toggleInputGroupOpenState && toggleInputGroupOpenState(stage.name || '');
          }}
          headerContentWhenClosed={
            <>
              {areAnyFocusedInputs && <div className="ml-auto mr-2 rounded bg-gray-200 text-gray-500 text-sm py-[1px] px-2">Has focus selections</div>}
            </>
          }
          padContentTop={true}
        >
          {stageContent}
        </Accordion>
      }
    </>
    
  )
}, areStagePropsEqual)

export const PathwayCreator1Page = ({
  comparisonIndex,
  arrayOfComparisonCaseInputHandlers,
  stages,
  // pathwayCreatorState,
  // setPathwayCreatorState,
}: {
  comparisonIndex: number;
  arrayOfComparisonCaseInputHandlers: UnifiedLCATEAComparisonCaseInputHandler[]; // TODO create type
  stages: any[];
  // pathwayCreatorState: PathwayCreatorState;
  // setPathwayCreatorState: React.Dispatch<React.SetStateAction<PathwayCreatorState>>;
}) => {

  const {
    allStage: { edges: allStageNodes },
    allLink: { edges: links },
    allAnalysis: { nodes: teaEnabledAnalyses },
  } = useAppMetadata();
  
  const inputHandler = arrayOfComparisonCaseInputHandlers[comparisonIndex];

  const { comparisonCases, isComparisonMode } = React.useContext(ModuleStateContext);
  const comparisonCase = comparisonCases?.[comparisonIndex];
  const isFocusModeActive = comparisonCase?.isFocusModeActive;
  const focusedInputs = comparisonCase?.focusedInputs;

  const expandInputAccordionsByDefault = useSettingValue('expandInputAccordionsByDefault');

  const [inputGroupOpenStates, setInputGroupOpenStates] = React.useState<Record<string, boolean>>(comparisonCases?.[comparisonIndex]?.data?.inputGroupOpenStates || {})

  const clearInputGroupOpenStates = () => {
    setInputGroupOpenStates({})
  }

  const toggleInputGroupOpenState = (name: string) => {
    setInputGroupOpenStates(prevStates => {
      return {
        ...prevStates,
        [name]: !(prevStates[name] ?? expandInputAccordionsByDefault),
      }
    })
  }

  // clean up this case's paths from pathsByCaseId atom (currently used for tracking whether to disable/hide focus link button when different paths are loaded simultaneously)
  useUnmount(() => {
    if (comparisonCase?.id) {
      setPathsByCaseId(pathsByCaseId => pathsByCaseId.filter(pathObj => pathObj.caseId !== comparisonCase?.id))
    }
  })

  const [pathsByCaseId, setPathsByCaseId] = useAtom(pathsByCaseIdAtom)

  const savedInputValuesByStage: StageInputValues[] = comparisonCase?.data?.customData?.inputValuesByStage;

  const stageNameArray = stages.map(stage => stage.name);
  const enduseStageIndex = stageNameArray.indexOf('Enduse');
  const processStageIndex = stageNameArray.indexOf('Process');
  const upstreamStageIndex = stageNameArray.indexOf('Upstream');

  const teaEnabledPathwayTuples = React.useMemo(() => {
    const pathwayTuples: string[][] = [];
    teaEnabledAnalyses.forEach(analysis => {
      const pathwayId = analysis.analysis.pathway_id;
      if (typeof pathwayId?.[0] === 'object') { // sometimes the pathway ID returned by backend metadata is an array of tuples, rather than just a tuple
        pathwayId.forEach(actualId => {
          pathwayTuples.push(actualId) as string[];
        })
      } else {
        pathwayTuples.push(pathwayId);
      }
    });
    const contentfulPathwayTuples = pathwayTuples.filter(tuple => {
      return tuple[0] !== 'placeholder'
    })
    return contentfulPathwayTuples;
  }, [JSON.stringify(teaEnabledAnalyses)])

  // NOTE / FUTURE TODO: instead of loading all customInputValues from saved case data, for now we're ony directly loading startWith and productType, and we're inferring product and resource, because product and resource are currently supplied by backend metadata as string names (e.g. "Corn stover (with biogenic carbon accounting)"), rather than IDs, and these string names are subject to change/reformatting, which would at least partially break saved case loading. At some point, this should be fixed since it's hacky, and should not be inferred anymore, but instead directly loaded from saved case data.
  const savedCustomInputValues: CustomInputValues = comparisonCase?.data?.customData?.customInputValues;
  // const savedProductType = comparisonCase?.data?.customData?.customInputValues?.startWith;
  // let customInputValues: CustomInputValues = {
  //   startWith: comparisonCase?.data?.customData?.customInputValues?.startWith,
  //   selectedProductType: savedProductType,
  //   selectedProduct: stages?.[4]?.activities?.find(activity => activity.id === savedProductType)?.products?.[0],
  //   selectedResource: stages?.[0]?.activities?.find(activity => activity.id === savedInputValuesByStage?.[0].nodeChosen)?.name,
  // };
  
  const enduseStage = stages.find(stage => stage.name === 'Enduse');

  const upstreamStage = stages.find(stage => stage.name === 'Upstream');
  const allProducts: string[] = unique(enduseStage?.activities?.map(activity => activity.products).flat())?.sort() || [];
  const allResources: string[] = unique(enduseStage?.activities?.map(activity => activity.resources).flat())?.sort() || [];

  const initialPathwayCreatorState = (
    savedCustomInputValues
    ?
    {
      ...defaultPathwayCreatorState,
      ...savedCustomInputValues,
    }
    :
    {
      ...defaultPathwayCreatorState,
      filteredProducts: allProducts,
    }
  );

  const [additionalBackendInputValues, setAdditionalBackendInputValues] = React.useState<Record<string, boolean>>({compute_cost: true})

  inputHandler.additionalBackendInputValues = additionalBackendInputValues;

  // create local state and copy it to inputHandler so we can access it from parent component (UnifiedLCATEA) when batch saving
  const [pathwayCreatorState, setPathwayCreatorState] = React.useState<PathwayCreatorState>(initialPathwayCreatorState)
  inputHandler.pathwayCreatorState = pathwayCreatorState;

  const {
    startWith,
    selectedProduct,
    selectedProductType,
    selectedResource,
    filteredProducts,
    filteredProductTypes,
    filteredResources,
    nodesChosen,
    dataSourcesChosen,
    nodeOptionsAtEachStage,
    farthestAutomaticallyTraversedStageIndex,
  } = pathwayCreatorState

  const isTeaEnabledForThisPathway = React.useMemo(() => {
    let isEnabled = false;
    if (nodesChosen.length === enduseStageIndex + 1) {
      const currentPathwayTuple = [nodesChosen[enduseStageIndex], nodesChosen[processStageIndex], nodesChosen[upstreamStageIndex]]
      const stringifiedTeaEnabledPathwayTuples = teaEnabledPathwayTuples.map(tuple => JSON.stringify(tuple));
      if (stringifiedTeaEnabledPathwayTuples.includes(JSON.stringify(currentPathwayTuple))) {
        isEnabled = true;
      }
    }
    return isEnabled;
  }, [nodesChosen])

  const [error, setError] = React.useState('');

  React.useEffect(() => {
    if (error) {
      customAlert({message: error, type: 'error'})
    }
    setError('')
  }, [error])

  useMakeSureSomeInputsAreVisibleAtIndex({
    comparisonIndex,
    getCustomAreAnyInputsVisible: () => {
      const areAnyInputValuesLoadedYet = inputHandler.arrayOfStageInputHandlers.some(({ inputStates }) => {
        const inputKeysInStage = Object.keys(inputStates || {})
        return inputKeysInStage.length > 0
      })
      if (!areAnyInputValuesLoadedYet) {
        return true // if input values are not loaded yet, just return true (i.e. there are some visible inputs), so we don't trip the alarm to disable focus mode
      }
      
      const areNoFocusedInputs = !focusedInputs || focusedInputs.length === 0;
      const areAnyInputsVisible = inputHandler.arrayOfStageInputHandlers.some(({ inputStates }) => {
        const inputKeysInStage = Object.keys(inputStates || {})
        return inputKeysInStage.some(key => focusedInputs?.includes(key) && inputStates[key].isVisible)
      })
      return areAnyInputsVisible 
    },
  })

  // const dataSourceVersionsForNodesChosen = dataSourcesChosen.map(dataSourceId => {
  //   const allDataSourceVersions = getCurrentDataSourceVersions({stages})
  //   return getDataSourceVersion({dataSourceId, allDataSourceVersions })
  // }) 
  // console.log(dataSourcesChosen)
  // console.log(dataSourceVersionsForNodesChosen)

  const isCaseStale = React.useMemo(() => {
    let isStale = false;
    const isCaseSaved = !!comparisonCase?.data
    if (isCaseSaved) {
      const savedCaseDataSourceVersions: Array<number | null> = comparisonCase?.data?.customData?.customInputValues?.dataSourceVersions;
      const savedDataSources = comparisonCase?.data?.customData?.customInputValues?.dataSourcesChosen;
      const currentDataSourceVersionsFromMetadata = getCurrentDataSourceVersions({stages})
      const areThereAnyVersionMismatches = savedCaseDataSourceVersions?.some((savedVersion, index) => {
        const savedDataSourceId = savedDataSources[index]
        const thisDataSourceVersionFromMetadata = getDataSourceVersion({
          dataSourceId: savedDataSourceId,
          allDataSourceVersions: currentDataSourceVersionsFromMetadata
        })
        return savedVersion !== thisDataSourceVersionFromMetadata
      })
      if (
        (areThereAnyVersionMismatches || !savedCaseDataSourceVersions)
        &&
        !comparisonCase?.isDemo
      ) {
        isStale = true;
      }
    }
    return isStale;
  }, [comparisonCase])

  useInvalidateStaleCases({ customIsCaseStale: isCaseStale, comparisonIndex })

  const runCaseAtIndex = useRunCaseAtIndex()

  const dispatch = React.useContext(ModuleDispatchContext);

  inputHandler.arrayOfStageInputHandlers = stages.map((stage, index) => {
    const activityAtThisStage = stage.activities?.find(activity => { return activity.id.indexOf(nodesChosen[index]) > -1 })
    const dataSourceChosenAtThisStage = dataSourcesChosen[index];
    const defaultDataSource = activityAtThisStage?.sources[0];
    const currentDataSource = (
      dataSourceChosenAtThisStage
      ?
      activityAtThisStage?.sources?.find(source => source.id === dataSourceChosenAtThisStage)
      :
      defaultDataSource
    );
    const userInputsAtThisStage = currentDataSource?.user_inputs;
    const currentDataSourceId = currentDataSource?.id;
    const initialInputValues = savedInputValuesByStage?.[index]?.inputValues;
    const [inputStates, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(
      userInputsAtThisStage,
      currentDataSourceId,
      undefined,
      initialInputValues,
      additionalBackendInputValues,
      { isSourceRequired: true }
    );
    return { inputStates, setInput, isValid, setInputError };
  })

  inputHandler.nodesChosen = nodesChosen;

  const arrayOfStageInputHandlers = inputHandler.arrayOfStageInputHandlers;

  const areCustomInputsValid = !!selectedProduct && !!selectedProductType && !!selectedResource

  const areUserInputsValid = arrayOfStageInputHandlers.every(inputHandler => {
    let isValid = false;
    const doesThisStageHaveInputs = Object.keys(inputHandler.inputStates)?.length > 0;
    if (doesThisStageHaveInputs) {
      isValid = inputHandler.isValid;
    } else {
      isValid = true;
    }
    return isValid;
  });

  const areInputsValid = areCustomInputsValid && areUserInputsValid;

  const handleRun = () => {

    const indicator = 'GWP';
    // let stages = [...allStageNodes];
    // stages = stages.map(stageNode => {
    //   return stageNode.node;
    // }).reverse(); // b/c starting with upstream by default now

    const { nodesChosen, arrayOfStageInputHandlers } = inputHandler;
    if (!nodesChosen) {
      return null;
    }
    const pathway = {
      name: getCaseNameFromComparisonCaseAtIndex(comparisonCase, comparisonIndex),
      steps: stages?.map((stage, index) => {
        let step;
        const nodeChosenAtThisStage = nodesChosen[index];
        if (nodeChosenAtThisStage !== null) {
          const inputStates = arrayOfStageInputHandlers[index].inputStates;
          const inputKeys = inputStates ? Object.keys(inputStates) : [];
          const inputStatesAsArray = inputKeys.map(key => ({ ...inputStates[key], name: key }) );
          step = {
            source_id: dataSourcesChosen[index] || stage.activities?.find(activity => activity.id === nodesChosen[index])?.sources[0].id,
            user_inputs: inputStatesAsArray.filter(inputState => inputState.isVisible).map(inputState => {
              return (
                !Number.isNaN(parseFloat(inputState.value))
                ? parseFloat(inputState.value)
                : inputState.value
              )
            }),
          }
        }
        return step;
      }).filter(step => !!step && !!step.source_id).reverse() // filter out null/undefined steps - don't want to send these to backend for analysis
    }

    const body = {
      indicator,
      pathways: [pathway],
      context: additionalBackendInputValues,
    }

    const customRequests: APIRequestWithType[] = [
      {
        type: 'LCA',
        endpoint: '/lca/analysis',
        body: body,
      },
    ]

    const shouldPerformTEA = isTeaEnabledForThisPathway && additionalBackendInputValues['compute_cost'];

    if (shouldPerformTEA) {
      customRequests.push({
        type: 'TEA',
        endpoint: '/tea/analysis',
        body: {
          pathway: body.pathways[0]
        },
      })
    }

    runCaseAtIndex({
      comparisonIndex,
      comparisonCase,
      customRequests,
      customData: {
        customInputValues: getCustomInputValues({inputHandler, stages}),
      },
      isValid: areInputsValid && !error,
      setError: setError,
      dispatch: dispatch,
    })
  }

  const getCustomData = () => {

    return {
      inputValuesByStage: getInputValuesByStage({
        stages,
        arrayOfStageInputHandlers,
        nodesChosen,
      }),
      customInputValues: getCustomInputValues({inputHandler, stages}),
    }
  }


  const handleSave = () => {
    dispatch({
      type: 'saveCaseAtIndex',
      index: comparisonIndex,
      value: {
        customData: getCustomData(),
      },
      dispatch: dispatch // have to send this b/c we have to call dispatch asynchronously from inside comparableResultsModule > reducer, but it doesn't have access to dispatch by itself
    })
  }

  const handleDuplicate = (): void => {
    dispatch({
      type: 'duplicateCaseAtIndexWithData',
      index: comparisonIndex,
      value: {
        customData: getCustomData(),
        inputGroupOpenStates: inputGroupOpenStates,
      }
    })
  }

  useRunAndSaveCaseEventListeners(handleRun, handleSave, comparisonIndex, handleDuplicate);

  const getProductsFilteredBy = ({
    selectedResource,
  }: {
    selectedResource?: string,
  }): string[] =>  {
    if (!selectedResource) {
      return [];
    }
    const possibleUpstreamNodesWithSelectedResource = upstreamStage.activities?.filter(activity => {
      return activity.resources?.includes(selectedResource);
    });
    const possibleProductsFromThoseUpstreamNodes = unique(possibleUpstreamNodesWithSelectedResource?.map(node => node.products).flat());  
    return possibleProductsFromThoseUpstreamNodes?.sort() || [];
  }

  const getProductTypesFilteredBy = ({
    selectedProduct,
    selectedResource,
  }: {
    selectedProduct?: string,
    selectedResource?: string,
  }): string[] => {
    let filteredProductTypes = enduseStage?.activities;
    if (!selectedProduct && !selectedResource) {
      return [];
    }
    if (selectedProduct) {
      filteredProductTypes = filteredProductTypes?.filter(activity => activity.products?.includes(selectedProduct))
    }
    if (selectedResource) {
      filteredProductTypes = filteredProductTypes?.filter(activity => activity.resources?.includes(selectedResource))
    }
    return filteredProductTypes?.map(activity => activity.name).sort() || [];
  }

  const getResourcesFilteredBy = ({
    selectedProductType
  }: {
    selectedProductType?: string
  }): string[] => {
    // filter resources
    if (!selectedProductType) {
      return [];
    }
    const possibleEnduseNodesWithSelectedProductType = enduseStage.activities?.filter(activity => {
      return activity.product_types?.includes(selectedProductType);
    });
    return unique(possibleEnduseNodesWithSelectedProductType?.map(node => node.resources).flat())?.sort() || [];
  }

  const chooseOptionFromArrayIfOneValueElseEmpty = (array: string[]) => {
    if (array.length === 1) {
      return array[0];
    } else {
      return '';
    }
  }

  const resetStagesWithState = (state: PathwayCreatorState) => {
    dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
    setError('');
    return {
      ...state,
      nodesChosen: [],
      dataSourcesChosen: [],
      nodeOptionsAtEachStage: [],
      farthestAutomaticallyTraversedStageIndex: 0,
    }
  }

  const resetStateInputs = (state: PathwayCreatorState) => {
    setError('');
    return {
      ...state,
      selectedProduct: '',
      selectedProductType: '',
      selectedResource: '',
    }
  }

  const setFarthestAutomaticallyTraversedStageIndex = (newIndex: number) => {
    setPathwayCreatorState(state => ({
      ...state,
      farthestAutomaticallyTraversedStageIndex: newIndex
    }))
  }

  const setNodesChosen = (newNodesChosen: Array<string | null>) => {
    setPathwayCreatorState(state => {
      return {
        ...state,
        nodesChosen: newNodesChosen,
      }
    })
    // update paths/nodes in our atom, for tracking whether focus link icon should be visible
    setPathsByCaseId(pathsByCaseId => {
      // if path exists already, update it, otherwise push it
      if (pathsByCaseId.find(pathObj => pathObj.caseId === comparisonCase?.id)) {
        const newPathsByCaseId = pathsByCaseId.map(pathObj => {
          if (pathObj.caseId === comparisonCase?.id) {
            return {
              ...pathObj,
              nodesChosen: newNodesChosen,
            }
          } else {
            return pathObj;
          }
        })
        return newPathsByCaseId
      } else {
        return pathsByCaseId.slice().concat([{
          nodesChosen: newNodesChosen,
          caseId: comparisonCase?.id,
        }])
      }
    })
  }

  const setDataSourcesChosen = (newDataSourcesChosen: Array<string | null>) => {
    setPathwayCreatorState(state => ({
      ...state,
      dataSourcesChosen: newDataSourcesChosen
    }))
  }

  const setNodeOptionsAtEachStage = (newNodeOptionsAtEachStage: string[][]) => {
    setPathwayCreatorState(state => ({
      ...state,
      nodeOptionsAtEachStage: newNodeOptionsAtEachStage
    }))
  }

  const setStartWith = (newStartWith: string, dontClearComparisonCase?: boolean) => {
    setPathwayCreatorState(state => {
      let newState = {
        ...state,
        startWith: newStartWith,
      }
      if (!dontClearComparisonCase) {
        newState = resetStagesWithState(newState);
        newState = resetStateInputs(newState);
      }
      if (newStartWith === 'product') {
        newState.filteredProducts = allProducts;
        newState.filteredProductTypes = [];
        newState.filteredResources = [];
      } else if (newStartWith === 'resource') {
        newState.filteredResources = allResources;
        newState.filteredProducts = [];
        newState.filteredProductTypes = [];
      } else {
        throw new Error('Neither product or resource selected - this should never happen!');
      }
      return newState;
    })
  }

  const setSelectedProduct = (newSelectedProduct: string , dontClearComparisonCase?: boolean) => {
    setPathwayCreatorState(state => {
      let newState = {
        ...state,
        selectedProduct: newSelectedProduct,
      }
      if (!dontClearComparisonCase) {
        newState = resetStagesWithState(newState);
      }
      if (newState.startWith === 'product') {
        // filter product types w/product
        newState.filteredProductTypes = enduseStage?.activities?.filter(activity => {
          return activity.products?.includes(newSelectedProduct);// && activity.resources?.includes(selectedResource);
        }).map(activity => activity.name).sort() || [];
        // if there's only one product type option, choose it, else keep it empty
        newState.selectedProductType = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredProductTypes);
        // if there's an automatically selected product type, filter/choose resources
        newState.filteredResources = getResourcesFilteredBy({selectedProductType: newState.selectedProductType});
        // if there's only one resource option, choose it, else keep it empty
        newState.selectedResource = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredResources);
      } else if (newState.startWith === 'resource') {
        // resource is already set so we don't need to address it
        // filter product types with product & resource
        newState.filteredProductTypes = getProductTypesFilteredBy({selectedProduct: newState.selectedProduct, selectedResource: newState.selectedResource});
        // if there's only one product type option, choose it, else leave it empty
        newState.selectedProductType = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredProductTypes);
      } else {
        throw new Error('Neither product or resource selected - this should never happen!');
      }
      return newState;
    })
  }

  const setSelectedProductType = (newSelectedProductType: string, dontClearComparisonCase?: boolean) => {
    setPathwayCreatorState(state => {
      let newState = {
        ...state,
        selectedProductType: newSelectedProductType,
      }
      if (!dontClearComparisonCase) {
        newState = resetStagesWithState(newState);
      }
      if (newState.startWith === 'product') {
        // filter resources based on product type
        newState.filteredResources = getResourcesFilteredBy({selectedProductType: newState.selectedProductType});
        // if there's only one resource option, choose it, else keep it empty
        newState.selectedResource = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredResources);
      } else if (newState.startWith === 'resource') {
        // resource is already set so we don't need to address it
        // filter product types with product & resource
        newState.filteredProductTypes = getProductTypesFilteredBy({selectedProduct: newState.selectedProduct, selectedResource: newState.selectedResource})
        // if there's only one product type option, choose it, else leave it empty
        newState.selectedProductType = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredProductTypes);
      } else {
        throw new Error('Neither product or resource selected - this should never happen!');
      }
      return newState;
    })
  }

  const setSelectedResource = (newSelectedResource: string, dontClearComparisonCase?: boolean) => {
    setPathwayCreatorState(state => {
      let newState = {
        ...state,
        selectedResource: newSelectedResource,
      }
      if (!dontClearComparisonCase) {
        newState = resetStagesWithState(newState);
      }
      if (newState.startWith === 'product') {
        // do nothing, since resource is the last in the filtering hierarchy in this flow
      } else if (newState.startWith === 'resource') {
        // filter products with resource
        newState.filteredProducts = getProductsFilteredBy({selectedResource: newState.selectedResource});
        // if there's only one product option, choose it, else leave it empty
        newState.selectedProduct = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredProducts);
        // if we've chosen a product, go on to product type
        if (newState.selectedProduct) {
          // filter product types with product & resource
          newState.filteredProductTypes = getProductTypesFilteredBy({selectedProduct: newState.selectedProduct, selectedResource: newState.selectedResource})
          newState.selectedProductType = chooseOptionFromArrayIfOneValueElseEmpty(newState.filteredProductTypes);
        } else {
          newState.filteredProductTypes = [];
          newState.selectedProductType = '';
        }
      } else {
        throw new Error('Neither product or resource selected - this should never happen!');
      }
      return newState;
    })
  }

  const handleStartWithChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const startWith = e.target.value;
    setStartWith(startWith);
    clearInputGroupOpenStates();
  }

  const handleProductChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const productName = e.target.value;
    setSelectedProduct(productName);
    clearInputGroupOpenStates();
  }

  const handleProductTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const productType = e.target.value;
    setSelectedProductType(productType);
    clearInputGroupOpenStates();
  }

  const handleResourceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newResource = e.target.value;
    setSelectedResource(newResource);
    clearInputGroupOpenStates();
  }

  const setNodeChosenAtIndex = (nodeChosen: string | null, index: number) => {
    if (index > (stages.length - 1)) {
      throw new Error('setNodeChosenAtIndex - stage index ' + index + ' out of bounds')
    }
    let newNodesChosen = [...nodesChosen.slice(0, index)];
    newNodesChosen.push(nodeChosen); // TODO fix this if we're going back in stage history and changing an option back there
    let newNodeOptionsAtEachStage = [...nodeOptionsAtEachStage.slice(0, index + 1)];
    let newDataSourcesChosen = [...dataSourcesChosen.slice(0, index)];
    newDataSourcesChosen.push(null);
    setNodesChosen(newNodesChosen);
    setDataSourcesChosen(newDataSourcesChosen);
    setNodeOptionsAtEachStage(newNodeOptionsAtEachStage);
    // this is a hack to force traverseGraph() again, otherwise we'd be setting farthestAutomaticallyTraversedStageIndex to the same value as before if we're choosing a different stage option without advancing, and then farthestAutomaticallyTraversedStageIndex wouldn't be actually changing, which wouldn't trigger useEffect and traverseGraph
    if (index === farthestAutomaticallyTraversedStageIndex) {
      setFarthestAutomaticallyTraversedStageIndex(index + 1);
    } else {
      setFarthestAutomaticallyTraversedStageIndex(index);
    }
  }

  const setDataSourceChosenAtIndex = (dataSourceChosen: string | null, index: number) => {
    const newDataSourcesChosen = [...dataSourcesChosen];
    newDataSourcesChosen[index] = dataSourceChosen;
    setDataSourcesChosen(newDataSourcesChosen);
  }

  React.useEffect(() => {
    const shouldTraverseGraph = (
      selectedProduct
      &&
      selectedProductType
      &&
      selectedResource
      &&
      nodesChosen.length < enduseStageIndex
    );
    if (shouldTraverseGraph) {
      traverseGraph();
    }
  }, [pathwayCreatorState])

  // Handle case loading - propagate custom inputs with saved data (startwith, product, product type, resource) and traverse graph
  React.useEffect(() => {
    if (savedCustomInputValues && !nodesChosen.length) {
      setStartWith(savedCustomInputValues.startWith, true);
      switch (startWith) {
        case 'product':
          setSelectedProduct(savedCustomInputValues.selectedProduct, true);
          setSelectedProductType(savedCustomInputValues.selectedProductType, true);
          setSelectedResource(savedCustomInputValues.selectedResource, true);
          break;
        case 'resource':
          setSelectedResource(savedCustomInputValues.selectedResource, true);
          setSelectedProduct(savedCustomInputValues.selectedProduct, true);
          setSelectedProductType(savedCustomInputValues.selectedProductType, true);
          break;
        default:
          break;
      }
      setAdditionalBackendInputValues(savedCustomInputValues.additionalBackendInputValues)
      setDataSourcesChosen(savedCustomInputValues.dataSourcesChosen);
    }
  }, [savedCustomInputValues])

  const traverseGraph = () => {

    const nodeOptionsAtCurrentStage = nodeOptionsAtEachStage[farthestAutomaticallyTraversedStageIndex];

    const hasNodeBeenChosenAtThisStage = !!nodesChosen[farthestAutomaticallyTraversedStageIndex];
    const stillNeedToChooseFromMultiplePossibleNodeAtThisStage = !hasNodeBeenChosenAtThisStage && nodeOptionsAtCurrentStage?.length > 0;
    if (stillNeedToChooseFromMultiplePossibleNodeAtThisStage) {
      return null;
    }

    // start traversing stages at current index, and get as far as we can until we run into multiple possibilities of next possible node - then dispay a dropdown
    let mostRecentNonNullNodeChosen = nodesChosen?.filter(node => !!node).slice(-1)?.[0];
    let previousNodeId = mostRecentNonNullNodeChosen || '';
    let newNodesChosen = [...nodesChosen];
    let newDataSourcesChosen = [...dataSourcesChosen];
    let newNodeOptionsAtEachStage = [...nodeOptionsAtEachStage];
    let farthestAutomaticallyTraversedNodeIndex = 0;

    loop1:
      for (let index = farthestAutomaticallyTraversedStageIndex; index <= enduseStageIndex; index++) {

        const currentStage = stages[index];        
        const isFirstStage = index === upstreamStageIndex;

        const isNodeAlreadyChosenAtThisStage = !!nodesChosen[index];
        if (isNodeAlreadyChosenAtThisStage) {
          // console.log ('node already chosen at this stage, skipping!');
          continue;
        }

        // if we're at a stage with no activities that match selected product type,
        // e.g. in midstream there are no "solar" containing activites,
        // then push chosen node id of null and go to next stage
        const activityIdsMatchingResourceAtThisStage = currentStage.activities?.filter(activity => {
          return activity.resources?.includes(selectedResource)
        }).map(activity => activity.id);

        // this includes all nodes that were linked to from previous chosen (non-null) node
        const nodeIdsLinkedFromLastChosenNonNullNode = links.filter(link => { // links are formatted for "starting with enduse" direction, so we have to read them backwards here
          return link.node.end === previousNodeId;
        }).map(link => {
          return link.node.start
        });

        // const allActivityIdsAtThisStage = currentStage.activities?.map(activity => activity.id);
        let possibleNodesAtThisStage = currentStage.activities?.filter(activity => {
          return nodeIdsLinkedFromLastChosenNonNullNode.includes(activity.id);
        }).filter(activity => { // filter possible nodes at this stage based on selected product and product type
          let isPossible = true;
          if (selectedProduct && !activity.products?.includes(selectedProduct)) {
            isPossible = false;
          }
          if (!activity.product_types?.includes(selectedProductType)) {
            isPossible = false;
          } else {
            // console.log('does match product type');
          }
          return isPossible;
        }) || [];

        let possibleNodeIdsAtThisStage = possibleNodesAtThisStage?.map(node => node.id) as string[] | undefined;

        // if we're in the very first stage, we choose based on activities that match product type (e.g. solar), because there are no previous nodes yet to link from
        possibleNodeIdsAtThisStage = (
          isFirstStage
          ?
          activityIdsMatchingResourceAtThisStage
          :
          possibleNodeIdsAtThisStage
        )

        farthestAutomaticallyTraversedNodeIndex = index;

        // if there are no possible nodes, go to next stage without choosing a node (null)
        if (possibleNodeIdsAtThisStage?.length === 0) {
          if (activityIdsMatchingResourceAtThisStage?.length === 0) {
            if (newNodesChosen.length < stages.length) {
              newNodesChosen.push(null);
              newDataSourcesChosen.push(null);
              newNodeOptionsAtEachStage.push([]);
            }
          }
        }
        // if there's one possible node, choose it and go to next stage
        else if (possibleNodeIdsAtThisStage?.length === 1) {
          const nodeIdBeingChosen = possibleNodeIdsAtThisStage[0] as string;
          newNodesChosen.push(nodeIdBeingChosen);

          // choose default source for this node
          const defaultDataSourceForNode = currentStage.activities?.find(activity => activity.id === newNodesChosen[index])?.sources?.[0]?.id ?? null;
          newDataSourcesChosen.push(defaultDataSourceForNode);
          newNodeOptionsAtEachStage.push([nodeIdBeingChosen]);
          previousNodeId = nodeIdBeingChosen;
        }
        // if there's more than one possible node, display dropdown of options
        else {
          newNodeOptionsAtEachStage.push(possibleNodeIdsAtThisStage);
          break loop1;
        }
      }
    
    // update paths
    setNodesChosen(newNodesChosen)

    setPathwayCreatorState(state => ({
      ...state,
      // nodesChosen: newNodesChosen,
      dataSourcesChosen: newDataSourcesChosen,
      nodeOptionsAtEachStage: newNodeOptionsAtEachStage,
      farthestAutomaticallyTraversedStageIndex: farthestAutomaticallyTraversedNodeIndex
    }));
  }

  const startWithChooser = (
    <InputBlock>
      <Label className="col-span-2">Start with</Label>
      <Select id="user-inputs--select-start-with" onChange={handleStartWithChange} value={startWith}>
        {startWithOptions.map(option => (
          <option key={option} value={option} label={capitalStr(option)} />
        ))}
      </Select>
    </InputBlock>
  )

  const productChooser = (
    <InputBlock>
      <Label className="col-span-2">Product</Label>
      <Select id="user-inputs--select-product" onChange={handleProductChange} value={selectedProduct}>
        <option value="" disabled={true} label="Choose one" />
        {filteredProducts.map(product => (
          <option key={product} value={product} label={product} />
        ))}
      </Select>
    </InputBlock>
  )

  let shouldShowProductTypeChooser = filteredProductTypes.length > 0;
  if (filteredProductTypes.length === 1 && selectedProduct === filteredProductTypes[0]) {
    shouldShowProductTypeChooser = false;
  }
  const productTypeChooser = (
    <>
      {shouldShowProductTypeChooser && (
        <InputBlock>
          <Label className="col-span-2">Product type</Label>
          <Select id="user-inputs--select-product-type" onChange={handleProductTypeChange} value={selectedProductType}>
            <option value="" disabled={true} label="Choose one" />
            {filteredProductTypes.map(productType => (
              <option value={productType} label={productType} />
            ))}
          </Select>
        </InputBlock>
      )}
    </>
  )

  const resourceChooser = (
    <InputBlock>
      <Label className="col-span-2">Resource</Label>
      <Select id="user-inputs--select-resource" onChange={handleResourceChange} value={selectedResource}>
        <option value="" disabled={true} label="Choose one" />
        {filteredResources.filter(resource => resource !== "Hydropower").map(resource => (
          <option key={resource} value={resource} label={resource} />
        ))}
      </Select>
    </InputBlock>
  )

  return (
    <>
      <div className={`${isFocusModeActive ? '' : 'mb-2'} ${isComparisonMode ? 'mt-2' : ''}`}>
        {!isFocusModeActive &&
          startWithChooser
        }
        {startWith === 'product'
          ?
          <>
            {productChooser}
            {productTypeChooser}
            {selectedProduct && selectedProductType &&
              resourceChooser
            }
          </>
          :
          <>
            {resourceChooser}
            {selectedResource &&
              productChooser
            }
            {selectedProduct &&
              productTypeChooser
            }
          </>
        }
        {selectedProduct && selectedProductType && selectedResource && isTeaEnabledForThisPathway && !isFocusModeActive &&
          additionalBackendInputs.map(input => (
            <InputBlock key={input.name}>
              <Label className="col-span-2">{input.label}</Label>
              {input.type === 'toggle' &&
                <Toggle label="" id="compute-cost" className="my-1" value={additionalBackendInputValues[input.name]} setValue={(value) => {
                  setAdditionalBackendInputValues(previousValues => {
                    dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
                    setError('');
                    const newValues = {
                      ...previousValues,
                      [input.name]: value,
                    };
                    return newValues;
                  })}}
                />
              }
              {/* {input.type === 'select' &&
                <Select
                  value={additionalBackendInputValues[input.name]}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    setAdditionalBackendInputValues(previousValues => {
                      return {
                        ...previousValues,
                        [input.name]: newValue,
                      }
                    })
                  }}
                >
                  {input.options.map(option => (
                    <option value={option.value} label={option.label} />
                  ))}
                </Select>
              } */}
            </InputBlock>
            
          ))
        }
      </div>

      {stages.map((stage, index) => {
        return (
          <Stage
            key={index}
            stage={stage}
            stages={stages}
            index={index}
            nodesChosen={nodesChosen}
            focusedInputs={focusedInputs}
            nodeOptionsAtEachStage={nodeOptionsAtEachStage}
            dataSourcesChosen={dataSourcesChosen}
            setDataSourceChosenAtIndex={setDataSourceChosenAtIndex}
            setNodeChosenAtIndex={setNodeChosenAtIndex}
            stageInputHandler={arrayOfStageInputHandlers[index]}
            comparisonIndex={comparisonIndex}
            isOpen={inputGroupOpenStates[stage.name] ?? expandInputAccordionsByDefault}
            // setIsOpen={}
            toggleInputGroupOpenState={toggleInputGroupOpenState}
          />
        )
      })}

      {error !== "" ? (
        <div className="text-red-700">
          Sorry, there was an error running this analysis
        </div>
      ) : null}
    </>
  )
}
