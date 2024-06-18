import * as React from "react";
import { db, getUniqueIncrementedCaseNamesForModule, promptUniqueBatchNameForModule } from "../hooks/useDB";
import { useEventListener } from "../hooks/useEventListener";
import { useRunAndSaveCaseEventListeners } from "../hooks/useRunAndSaveCaseEventListeners";
import useUserInputs, { getInputValuesRecordFromInputStates } from "../hooks/useUserInputs";
import { trigger } from "../utils/events";
import { ComparisonRow, ModuleDispatchContext, ModuleStateContext, saveBatch, useRunCaseAtIndex } from "./comparableResultsModule";
import { customAlert } from "./customAlert";
import { SavedItemMenu } from "./savedItemMenu";
import UserInputs from "./userInputs";
import { SavedBatchControls } from "./savedBatchControls";
import client from "../utils/client";
import { useSetting, useSettingValue } from "../hooks/useSettings";
import { Loader } from "./styles";
import { useMakeSureSomeInputsAreVisibleAtIndex } from "../hooks/useMakeSureSomeInputsAreVisibleAtIndex";
import { useInvalidateStaleCases } from "../hooks/useInvalidateStaleCases";

export const ComparisonInputHandlerContext = React.createContext<Partial<InputHandler[]>>([]);

export const ComparisonInputHandler = ({
  moduleMetadata,
  apiPathOverride,
  extraContentByCase,
  source = undefined,
}: {
  moduleMetadata: BasicModuleMetadata;
  apiPathOverride?: string;
  extraContentByCase?: JSX.Element[];
  source?: undefined | string;
}): JSX.Element => {

  const moduleState = React.useContext(ModuleStateContext) as ModuleStateProps;
  const { comparisonCases, isComparisonMode, maxComparisonCases, type, apiPath } = moduleState;
  const [hasLoadedDynamicModuleMetadata, setHasLoadedDynamicModuleMetadata] = React.useState(false)

  const dispatch = React.useContext(ModuleDispatchContext);

  const apiEndpoint = `${apiPathOverride || apiPath}/analysis`;

  if (!apiEndpoint) {
    throw new Error('No API endpoint provided in module definition')
  }

  // allow for dynamic metadata fetching instead of static metadata built during frontend build (for accelerating backend user_input changes in modules)
  const dynamicallyFetchModuleMetadata = useSettingValue('dynamicallyFetchModuleMetadata');
  const [metadata, setMetadata] = React.useState<Partial<BasicModuleMetadata>>(dynamicallyFetchModuleMetadata ? {user_inputs: [], hash: ''} : moduleMetadata);
  
  const fetchMetadata = () => {
    client(`${apiPathOverride || apiPath}/metadata`).then(response => {
      const transformedMetadata = {
        user_inputs: (response as BasicModuleMetadata).user_inputs?.map(mapUserInputs),
        hash: (response as BasicModuleMetadata).hash,
      }
      setMetadata(transformedMetadata);
      setHasLoadedDynamicModuleMetadata(true);
    });
  }
  
  React.useEffect(() => {
    if (dynamicallyFetchModuleMetadata && !hasLoadedDynamicModuleMetadata) {
      fetchMetadata()
    }
  }, [metadata, dynamicallyFetchModuleMetadata, hasLoadedDynamicModuleMetadata])

  React.useEffect(() => {
    if (dynamicallyFetchModuleMetadata) {
      fetchMetadata();
    } else {
      setMetadata(moduleMetadata)
    }
  }, [apiPathOverride])

  const arrayOfComparisonCaseInputHandlers = new Array(maxComparisonCases).fill(null).map((o, comparisonIndex) => {
    const [inputStates, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(
      metadata.user_inputs,
      source,
      apiPathOverride || apiPath,
      comparisonCases?.[comparisonIndex]?.data?.inputValues,
    );

    return {
      inputStates,
      setInput,
      isValid,
      setInputError,
    };
  });

  const attemptToRunAllCases = () => {
    const caseIndexesWithValidInputs: number[] = [];
    arrayOfComparisonCaseInputHandlers.forEach((inputHandler, comparisonIndex) => {
      const areInputsValid = inputHandler.isValid;
      const isThisCaseActive = comparisonCases?.length && comparisonIndex < comparisonCases?.length;
      const isThisCaseAlreadyRun = !!comparisonCases?.[comparisonIndex]?.data?.analysisResult;
      if (areInputsValid && isThisCaseActive && !isThisCaseAlreadyRun) {
        caseIndexesWithValidInputs.push(comparisonIndex);
      }
    });
    if (!caseIndexesWithValidInputs.length) {
      customAlert({message: 'No cases to run. All cases either have already been run, or have invalid inputs.'})
    }
    caseIndexesWithValidInputs.forEach(caseIndex => {
      trigger('runCase', { comparisonIndex: caseIndex })
    })
  }

  const handleSaveBatch = () => {
    saveBatch({
      moduleType: type,
      comparisonCases,
      unsavedCaseData: comparisonCases.map((comparisonCase, comparisonIndex) => {
        if (comparisonCase.isUnsaved) {
          return {
            inputStates: arrayOfComparisonCaseInputHandlers[comparisonIndex].inputStates,
            moduleVersion: metadata.version,
            hash: metadata.hash,
          }
        }
      }),
      dispatch,
    })
  }

  useEventListener('attemptToRunAllCases', attemptToRunAllCases)
  useEventListener('saveBatch', handleSaveBatch);

  if (!metadata) {
    return <Loader />
  }

  return (
    <ComparisonInputHandlerContext.Provider value={arrayOfComparisonCaseInputHandlers}>
      <ComparisonRow
        sidebar={
          <SavedBatchControls />
        }
        content={comparisonCases?.map((comparisonCase, comparisonIndex) => {
          return (
            <div
              key={comparisonCase.id}
              id={`inputs--case-${comparisonIndex}`}
              className={comparisonCase.isFocusModeActive && isComparisonMode ? 'pt-2' : ''}
            >
              <InputHandler
                comparisonIndex={comparisonIndex}
                metadata={metadata}
                inputHandler={arrayOfComparisonCaseInputHandlers[comparisonIndex]}
                apiEndpoint={apiEndpoint}
              />
              {extraContentByCase &&
                extraContentByCase[comparisonIndex]
              }
            </div>
          )
        })}
      />
    </ComparisonInputHandlerContext.Provider>
  )
}

export const InputHandler = ({
  comparisonIndex,
  metadata,
  apiEndpoint,
  inputHandler,
}: {
  comparisonIndex: number,
  metadata: BasicModuleMetadata,
  apiEndpoint: string,
  inputHandler: InputHandler,
}): JSX.Element => {
  const { comparisonCases } = React.useContext(ModuleStateContext);
  const dispatch = React.useContext(ModuleDispatchContext);
  const comparisonCase = comparisonIndex >= 0 ? comparisonCases?.[comparisonIndex] : null;
  const focusedInputs = comparisonCase?.focusedInputs;
  const {inputStates, setInput, isValid, setInputError} = inputHandler;

  const [error, setError] = React.useState<string>('');

  const [inputGroupOpenStates, setInputGroupOpenStates] = React.useState<Record<string, boolean>>(comparisonCase?.data?.inputGroupOpenStates || {})

  const expandInputAccordionsByDefault = useSettingValue('expandInputAccordionsByDefault');

  const toggleInputGroupOpenState = (name: string) => {
    setInputGroupOpenStates(prevStates => {
      return {
        ...prevStates,
        [name]: !(prevStates[name] ?? expandInputAccordionsByDefault),
      }
    })
  }

  useMakeSureSomeInputsAreVisibleAtIndex({
    comparisonIndex,
    inputStates,
  })

  // show error dialog on analysis running error
  React.useEffect(() => {
    if (error) {
      customAlert({message: error, type: 'error'})
    }
    setError('')
  }, [error])

  const runCaseAtIndex = useRunCaseAtIndex()

  const handleRun = () => {
    runCaseAtIndex({
      comparisonIndex,
      comparisonCase,
      apiEndpoint,
      inputStates,
      isValid: isValid && !error,
      setError,
      dispatch,
    })
  }

  const handleSave = () => {
    dispatch({
      type: 'saveCaseAtIndex',
      index: comparisonIndex,
      value: {
        inputStates, // we have to send inputStates here b/c they aren't tracked in moduleState yet, only in each module itself.
        hash: metadata.hash,
        moduleVersion: metadata.version,
      },
      dispatch: dispatch // have to send this b/c we have to call dispatch asynchronously from inside comparableResultsModule > reducer, but it doesn't have access to dispatch by itself
    })
  }

  const handleDuplicate = (): void => {
    console.log('duplicting with inputgroupopenstates:', inputGroupOpenStates)
    dispatch({
      type: 'duplicateCaseAtIndexWithData',
      index: comparisonIndex,
      value: {
        inputValues: getInputValuesRecordFromInputStates(inputStates),
        inputGroupOpenStates: inputGroupOpenStates,
      },
    })
  }

  useRunAndSaveCaseEventListeners(handleRun, handleSave, comparisonIndex, handleDuplicate);

  useInvalidateStaleCases({comparisonIndex, moduleMetadata: metadata})

  return (
    <>
      <UserInputs
        userInputs={metadata.user_inputs}
        comparisonIndex={comparisonIndex}
        inputStates={inputStates}
        inputGroupOpenStates={inputGroupOpenStates}
        toggleInputGroupOpenState={toggleInputGroupOpenState}
        setInput={(name, value, opts) => {
          setError("");
          if (!opts?.dontClearComparisonCase) {
            dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
          }
          setInput(name, value, opts);
        }}
        setInputError={setInputError}
      />
      {/* {error && (
        <div className="text-red-700">
          <br />
          {error}
        </div>
      )} */}
    </>
  )
}

const mapConditionals = (conditionals) => {
  // if the second arg in a conditional is not an array, return it in an array
  return conditionals.length > 0
    ? conditionals.map(({ args, ...rest }) => ({
        ...rest,
        args: [[args[0]], Array.isArray(args[1]) ? args[1] : [args[1]]],
      }))
    : [];
};

const mapUserInputs = (u) => ({
  ...u,
  options: u.options
    ? u.options.map(({ value, conditionals }) => ({
        // toString() all options (string | number)...
        // since the GraphQL spec does not support union scalar types:
        // https://github.com/graphql/graphql-spec/issues/215
        value: value.toString(),
        conditionals: mapConditionals(conditionals),
      }))
    : undefined,
  conditionals: mapConditionals(u.conditionals),
});
