import * as React from "react";
import * as Sentry from "@sentry/browser";
import { db, getUniqueIncrementedCaseNamesForModule, promptUniqueBatchNameForModule } from "../hooks/useDB";
import { getInputValuesRecordFromInputStates } from "../hooks/useUserInputs";
import { generateUniqueIntId, getHeaderTitle, triggerResize, unique } from "../utils";
import { maxComparisonResultCols } from "../utils/constants";
import { trigger } from "../utils/events";
import { customAlert } from "./customAlert";
import SEO from "./seo";
import useClient from "../hooks/useClient";
import { useAtomValue } from "jotai";
import { isFocusLinkingDisabledAtom } from "../store/store";

export const ModuleStateContext = React.createContext<Partial<ModuleStateProps>>({});
export const ModuleDispatchContext = React.createContext({} as React.Dispatch<ModuleActionProps>);

const getEmptyComparisonCase = (): ComparisonCase => ({
  id: generateUniqueIntId(),
  inputGroupOpenStates: {},
  focusedInputs: [],
});
const getEmptyComparisonCaseWithNullInputValues = (): ComparisonCase => {
  return {
    ...getEmptyComparisonCase(),
    data: {
      inputValues: {}
    }
  }
}

const areAllArrayElementsEqual = (arr: Array<unknown>) => arr.every(val => val === arr[0]);

const updateChartControlAllocation = (state: ModuleStateProps): ModuleStateProps => {
  const existentComparisonCaseIds = state.comparisonCases?.filter(c => !!c.data?.analysisResult).map(c => c.savedCaseId || c.id);
  const areAllComparisonResultsTheSame = areAllArrayElementsEqual(existentComparisonCaseIds);
  const chartControlAllocation = areAllComparisonResultsTheSame ? 'individual' : 'group';
  return {
    ...state,
    chartControlAllocation: chartControlAllocation
  }
}

const addComparisonCol = (state: ModuleStateProps): ModuleStateProps => {
  triggerResize();
  let newState: ModuleStateProps = {
    ...state,
    isComparisonMode: true,
    comparisonCases: [...state.comparisonCases].concat([getEmptyComparisonCaseWithNullInputValues()]),
    numChartCols: 1,
    isAnyColumnFullscreened: false,
  };
  newState = alignCaseFocusStates(newState);
  return newState;
}

/**
 * Align comparison case focus states.
 * This should only do anything if focus link is active.
 * 
 * @param state 
 * @returns 
 */
const alignCaseFocusStates = (state: ModuleStateProps): ModuleStateProps => {
  if (!state.isFocusLinkActive) {
    return state;
  }
  const prototypeCasesWithFocusedInputs = state.comparisonCases.filter(c => c.focusedInputs && c.focusedInputs.length > 0);
  const prototypeCase = prototypeCasesWithFocusedInputs?.[0]
  if (prototypeCase) {
    const prototypeCaseIndex = state.comparisonCases.indexOf(prototypeCase)
    const newState = {
      ...state,
      comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
        if (index === prototypeCaseIndex) {
          return comparisonCase;
        } else {
          return {
            ...comparisonCase,
            focusedInputs: prototypeCase.focusedInputs,
            isFocusModeActive: prototypeCase.isFocusModeActive,
          }
        }
      })
    }
    return newState;
  } else {
    return state;
  }
}

export const getCaseNameFromComparisonCaseAtIndex = (comparisonCase: ComparisonCase | undefined, index: number) => {
  return comparisonCase?.name || `New Case ${index + 1}`;
}

const reducer = (state: ModuleStateProps, action: ModuleActionProps): ModuleStateProps => {
  if (process.env.NODE_ENV === 'development') {
    console.log('REDUCER: ', action);
  }
  let newState: ModuleStateProps;
  let newComparisonCases: ComparisonCase[];
  switch (action.type) {
    case 'setSubModuleType':
      return {
        ...state,
        subModuleType: action.value
      }
    case 'setColumnFullscreen':
      const isSettingToFullscreen = action.value
      // setIsSidebarOpenWithNewSidebarAndFullscreenState(wasSidebarSetOpen, action.value as boolean);
      return {
        ...state,
        isAnyColumnFullscreened: isSettingToFullscreen as boolean,
        numChartCols: isSettingToFullscreen ? 3 : 1
      };
    case 'setNumChartCols':
      return { ...state, numChartCols: action.value as number };
    case 'addComparisonCol':
      // newState = { ...state };
      newState = addComparisonCol(state);
      newState = updateChartControlAllocation(newState);
      return newState;
    case 'setIsCaseLoadingAtIndex':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index !== action.index) {
            return comparisonCase;
          }
          return {
            ...comparisonCase,
            isLoading: action.value,
          }
        })
      };
    case 'setComparisonCaseIdAtIndex':
      var id = action.value;
      // reformat id from select option value to proper value - e.g. we don't want '' empty string, we want null instead (for proper downstream functionality based on null id value)
      switch (id) {
        case '':
          id = null;
          break;
        case 'unsaved':
          break;
        default:
          break;
      }
      const isIdFromSavedCase = id !== null && id !== 'unsaved';
      if (isIdFromSavedCase) {
        db.savedCases
          .where('id')
          .equals(id)
          .with({ data: 'savedCaseData' })
          .then(savedCases => {
            const thisCase = savedCases?.[0];
            action.dispatch && action.dispatch({
              type: 'setComparisonCaseAtIndex',
              index: action.index,
              value: {
                ...thisCase,
                id: generateUniqueIntId(), // this needs to be new every time, even when loading a saved case, becuase the input handler for each case uses this id as a key - we can't have duplicate keys if we load the same case in two different columns!
                name: thisCase?.name,
                data: thisCase?.data?.[0],
                savedCaseId: id,
                // isLoading: false,
              }
            })
          })
      }
      newState = {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index !== action.index) {
            return comparisonCase;
          }
          return {
            id: id,
            isLoading: isIdFromSavedCase
          }
        })
      }
      // clear batch if this case ID doesn't match one in current batch (if there is one)
      // debugger
      if (newState.savedBatch?.caseIds && !newState.savedBatch.caseIds.includes(id)) {
        delete newState.savedBatch;
      }
      newState = updateChartControlAllocation(newState);
      return newState;
    case 'setComparisonCasePropsAtIndex':
      newState = modifyCaseByIndexWithProps(state, action.index, action.value);
      return newState;
    case 'resetComparisonCaseAtIndex':
      newState = {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index === action.index) {
            return getEmptyComparisonCaseWithNullInputValues()
          } else {
            return comparisonCase
          }
        })
      }
      newState = updateChartControlAllocation(newState)
      newState = alignCaseFocusStates(newState)
      return newState
    case 'setComparisonCaseAtIndex':
      newState = {
        ...state
      };
      if (newState.comparisonCases.length <= action.index) {
        newState = addComparisonCol(newState);
      }
      
      newState.comparisonCases[action.index] = action.value;
      // if this newly loaded case's id isn't in active batch, clear the batch (if there is one)
      if (newState.savedBatch?.caseIds && !newState.savedBatch.caseIds.includes(action.value.savedCaseId || action.value.id)) {
        delete newState.savedBatch;
      }

      const newSubModuleType = action.value.subModuleType;

      if (newSubModuleType) {
        newState.subModuleType = newSubModuleType
      }
      
      // console.log(action.value.focusedInputs)
      // activate focus mode if...
      // if (action.value.isFocusModeActive && action.value.focusedInputs?.length > 0) {
      //   newState.comparisonCases[action.index].isFocusModeActive = true
      // }

      // if (newState.isFocusLinkActive) {

      // }
      // activate focus mode if all current cases have at least one focused input
      // if (newState.comparisonCases.every(comparisonCase => comparisonCase.focusedInputs && comparisonCase.focusedInputs.length > 0)) {
      //   newState.comparisonCases = newState.comparisonCases.map(c => c.isFocusModeActive = true) = true;
      // }
      // if (action.value.focusedInputs) {
      //   newState.focusedInputs = unique(newState.focusedInputs?.concat(action.value.focusedInputs) ?? []);
      // }
      newState = updateChartControlAllocation(newState);
      newState = alignCaseFocusStates(newState);
      // newState = checkSubModuleAlignment(newState);
      return newState;
    case 'setComparisonCaseDataAtIndex':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index !== action.index) {
            // This isn't the item we care about - keep it as-is
            return comparisonCase
          }
          // Otherwise, this is the one we want - return an updated value
          return {
            ...comparisonCase,
            isLoading: false,
            isRunning: false,
            data: action.value,
          } as ComparisonCase
        })
      }
    case 'deleteSavedCaseIds':
      const savedCaseIds = action.value;
      deleteSavedCaseIds(savedCaseIds);
      newComparisonCases = state.comparisonCases.slice().filter(comparisonCase => {
        return !savedCaseIds.includes(comparisonCase.savedCaseId)
      });
      newState = {
        ...state,
        comparisonCases: newComparisonCases,
      }
      if (newComparisonCases.length === 0) { // we just deleted all active cases, so reset comparisonCases to one empty case and clear saved batch if there is one
        newState.comparisonCases = [getEmptyComparisonCase()];
        delete newState.savedBatch;
      }
      return newState;
    case 'removeComparisonCaseAtIndex':
      // if we're removing the last one, just return an empty comparison case
      if (state.comparisonCases.length === 1) {
        newComparisonCases = [getEmptyComparisonCase()];
      } else {
        newComparisonCases = state.comparisonCases.slice().filter((item, index) => index !== action.index)
      }
      const isComparisonMode = newComparisonCases.length > 1 ? true : false;
      triggerResize();
      newState = {
        ...state,
        isComparisonMode: isComparisonMode,
        comparisonCases: newComparisonCases,
        savedBatch: undefined,
      };
      // if (newState.comparisonCases.length === 1) {
      //   newState.isFocusLinkActive = false
      // }
      newState = updateChartControlAllocation(newState);
      return newState;
    case 'clearComparisonCaseAtIndex': // but preserve current user input values
      if (typeof action.index !== 'number') {
        break;
      }
      const thisCase = state.comparisonCases[action.index];
      // const thisCaseKeys = Object.keys(thisCase);
      const isThisCaseAlreadyCleared = !thisCase?.data?.analysisResult && !thisCase?.data?.customData;
      // const isThisCaseAlreadyCleared = thisCaseKeys?.length === 1 && thisCaseKeys.includes('id'); // this means we only have an id stored (randomly generated), but no other saved case data)
      // const isThisCaseAlreadyCleared = JSON.stringify(state.comparisonCases[action.index]) === JSON.stringify(getEmptyComparisonCase());
      if (isThisCaseAlreadyCleared) {
        return state;
      }
      newState = {
        ...state,
        savedBatch: undefined,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index !== action.index) {
            return comparisonCase;
          }
          return {
            id: thisCase.id, // preserve the case id, because otherwise all input values will be cleared since input handler component uses this id as its key - and we want to retain input values when you change one input - we just want to clear the charts
            inputGroupOpenStates: thisCase.inputGroupOpenStates,
          };
        })
      }
      newState = updateChartControlAllocation(newState);
      newState = alignCaseFocusStates(newState);
      return newState;
    case 'resetComparisonCasesToOneEmptyCase':
      newState = {
        ...state,
        isComparisonMode: false,
        comparisonCases: [getEmptyComparisonCase()]
      }
      newState = updateChartControlAllocation(newState);
      return newState;
    case 'loadCaseIdAsDuplicateAtIndex':
      db.savedCases
        .where('id')
        .equals(parseInt(action.value))
        .with({ data: 'savedCaseData' })
        .then(savedCases => {
          const thisCase = savedCases?.[0];
          action.dispatch && action.dispatch({
            type: 'setComparisonCaseAtIndex',
            index: action.index,
            value: {
              id: generateUniqueIntId(), // this needs to be new every time, even when loading a saved case, becuase the input handler for each case uses this id as a key - we can't have duplicate keys if we load the same case in two different columns!
              data: {
                ...thisCase?.data?.[0],
                analysisResult: null,
              },
            }
          })
        })
      return state;
    case 'duplicateCaseAtIndexWithData':
      if (state.comparisonCases.length >= state.maxComparisonCases) {
        console.log(state)
        throw new Error('Can\'t duplicate case since we\'re already at the maximum number of cases');
      }
      let newData = action.value;
      if (!newData) {
        throw new Error('No data passed to duplicateCaseAtIndex dispatch action');
      }
      let dupe = JSON.parse(JSON.stringify(state.comparisonCases[action.index as number]));
      dupe.isUnsaved = true;
      if (dupe.id) {
        dupe.id = generateUniqueIntId(); // replace id if it exists, otherwise it's probably null, so leave it at that
      }
      if (!dupe.data) {
        dupe.data = newData;
      } else { // if case we're duping already had data, we still want to preserve input group open states
        dupe.data.inputGroupOpenStates = newData.inputGroupOpenStates || {};
      }
      if (newData.customData) {
        dupe.data.customData = newData.customData;
      }
      if (dupe.data) {
        dupe.data.analysisResult = null; // don't duplicate chart data, just inputs and name and such
      }
      delete dupe.name;
      // if (dupe.name) {
      //   dupe.name += ' copy';
      // }
      delete dupe.savedCaseId;
      delete dupe.data?.savedCaseId;
      delete dupe.data?.id;
      newState = {
        ...state,
        comparisonCases: state.comparisonCases.concat(dupe),
        isComparisonMode: true,
      }
      newState = updateChartControlAllocation(newState);
      triggerResize();
      return newState;
    case 'setCaseToRunningAtIndex':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (action.index !== index) {
            return comparisonCase;
          }
          return {
            ...comparisonCase,
            data: undefined,
            isRunning: true,
            highlightErroneousInputs: false,
          } as ComparisonCase
        })
      };
    case 'stopRunningCaseAtIndex':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (action.index !== index) {
            return comparisonCase;
          }
          return {
            ...comparisonCase,
            // data: undefined,
            isRunning: false,
          } as ComparisonCase
        })
      }
    case 'saveCaseAtIndex':
      if (typeof action.index !== 'number') break;
      const analysisResult = state.comparisonCases[action.index]?.data?.analysisResult;
      if (!analysisResult) {
        alert('Please run analysis before saving!');
        return state;
      }
      promptUniqueCaseNameForModule(state.type).then(name => {
        if (name) {
          saveCaseAtIndex({
            name,
            comparisonCases: state.comparisonCases,
            index: action.index,
            data: action.value,
            moduleType: state.type,
            subModuleType: state.subModuleType,
            dispatch: action.dispatch,
          })
        }
      })
      return state;
    // case 'clearAllFocusedInputs':
    //   newState = {
    //     ...state,
    //     comparisonCases: state.comparisonCases.map(c => {
    //       return {
    //         ...c,
    //         focusedInputs: []
    //       }
    //     }),
    //     isFocusModeActive: false,
    //   }
    //   return newState
    case 'setFocusedInputsAtIndex':
      const areWeClearingFocusedInputs = action.value.length === 0

      newState = {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (state.isFocusLinkActive && areWeClearingFocusedInputs) {
            return {
              ...comparisonCase,
              focusedInputs: [],
              isFocusModeActive: false,
            }
          } else {
            if (index === action.index) {
              return {
                ...comparisonCase,
                focusedInputs: action.value,
                isFocusModeActive: false,
              }
            } else {
              return comparisonCase;
            }
          }
        })
      }
      return newState;
    case 'toggleFocusInputAtCaseIndex':
      const inputName = String(action.value);
      let focusedInputsForCase = state.comparisonCases?.[action.index]?.focusedInputs?.slice() || [];
      const isInputAlreadyFocused = focusedInputsForCase.includes(inputName);
      const isFocusing = !isInputAlreadyFocused

      newState = {
        ...state,
        comparisonCases: [...state.comparisonCases].map((comparisonCase, comparisonIndex) => {
          // when focus link mode is active, also toggle this input focus state in all other active cases (same direction as we're doing it in the target case) - otherwise just return those cases unmodified
          if (!state.isFocusLinkActive && comparisonIndex !== action.index) {
            return comparisonCase;
          }
          let newFocusedInputs = comparisonCase?.focusedInputs?.slice() || [];
          if (isFocusing) {
            newFocusedInputs.push(inputName);
          } else {
            newFocusedInputs = newFocusedInputs.filter(input => input !== inputName)
          }
          return {
            ...comparisonCase,
            focusedInputs: unique(newFocusedInputs)
          }
        })
      }

      // if there are any cases with no focused inputs, disable focus mode
      if (!newState.comparisonCases.every(comparisonCase => comparisonCase?.focusedInputs && comparisonCase?.focusedInputs.length > 0)) {
        newState.isFocusModeActive = false;
      }

      // if (isInputAlreadyFocused) {
      //   focusedInputs = focusedInputs.filter(name => name !== inputName)
      // } else {
      //   focusedInputs.push(inputName);
      // }
      // newState = {
      //   ...state,
      //   focusedInputs: unique(focusedInputs) || [],
      // }
      // if (focusedInputs.length === 0) {
      //   newState.isFocusModeActive = false;
      // }
      return newState;
    case 'toggleFocusModeAtIndex':
      const isActivating = !state.comparisonCases?.[action.index]?.isFocusModeActive;
      // applyto all cases if focus linking isn't disabled, and if focus link is active

      const shouldApplyToAllCases = state.isFocusLinkActive && !action.options?.isFocusLinkingDisabled
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (shouldApplyToAllCases || index === action.index) {
            return {
              ...comparisonCase,
              isFocusModeActive: isActivating,
            }
          } else {
            return comparisonCase;
          }
        })
        // isFocusModeActive: !state.isFocusModeActive,
        // focusedInputs: isDeactivating ? [] : [...state.focusedInputs]
      }
    case 'disableFocusModeForAllCases':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map(comparisonCase => ({
          ...comparisonCase,
          isFocusModeActive: false,
        }))
      }
    case 'toggleInputGroupOpenStateAtComparisonIndex':
      return {
        ...state,
        comparisonCases: state.comparisonCases.map((comparisonCase, index) => {
          if (index !== action.index) {
            return comparisonCase;
          }
          if (!comparisonCase.inputGroupOpenStates) comparisonCase.inputGroupOpenStates = {}
          const wasInputGroupOpen = comparisonCase.inputGroupOpenStates?.[action.value];
          comparisonCase.inputGroupOpenStates[action.value] = !wasInputGroupOpen;
          return comparisonCase;
        })
      }
    case 'setIsFocusLinkActive':
      newState = {
        ...state,
        isFocusLinkActive: action.value,
      }
      newState = alignCaseFocusStates(newState)
      return newState
    case 'toggleIsFocusLinkActiveWithIndex':
      newState = {
        ...state,
        isFocusLinkActive: !state.isFocusLinkActive,
      }
      // if we're enabling focus link, duplicate this case's state to others
      if (newState.isFocusLinkActive) {
        const prototypeCase = state.comparisonCases?.[action.index]
        newState.comparisonCases = newState.comparisonCases.map((comparisonCase, index) => {
          // duplicate focus state to other active cases
          if (index !== action.index) {
            return {
              ...comparisonCase,
              focusedInputs: [...prototypeCase.focusedInputs ?? []],
              isFocusModeActive: prototypeCase.isFocusModeActive,
            }
          } else {
            return comparisonCase
          }
        })
      }
      return newState;
    case 'loadBatchId':
      const batchId = Number(action.value);
      if (typeof action.dispatch !== 'function') throw new Error('Dispatch function should have been passed into dispatch call')
      // newState = { ...state, }
      db.savedBatches.get(batchId).then((batch: ComparisonCaseBatch) => {
        action.dispatch({ type: 'setBatch', value: batch });
        // disable focus link if this state is saved with the batch (currently only possible for demo batches)
        if (batch.isFocusLinkActive === false) {
          action.dispatch({ type: 'setIsFocusLinkActive', value: false })
        }
        batch.caseIds.forEach((caseId, comparisonIndex) => {
          db.savedCases.get(caseId).then(savedCase => {
            action.dispatch({ type: 'setComparisonCaseIdAtIndex', index: comparisonIndex, value: savedCase?.id, dispatch: action.dispatch })
          });
        });
      });
      return state;
    case 'setBatch':
      const batch = action.value;
      newState = {
        ...state,
        savedBatch: batch,
      }
      return newState;
    case 'setBatchProps':
      const props = action.value;
      newState = {
        ...state,
        savedBatch: {
          ...state.savedBatch,
          ...props
        }
      }
      return newState;
    case 'deleteSavedBatchIds':
      const savedBatchIds = action.value;
      db.savedBatches.bulkDelete(savedBatchIds);
      console.log(savedBatchIds);
      newState = { ...state };
      if (state.savedBatch && state.savedBatch.id in savedBatchIds) {
        delete newState.savedBatch;
      }
      return newState;
    case 'enableErroneousInputHighlightingAtIndex':
      newState = modifyCaseByIndexWithProps(state, action.index, { highlightErroneousInputs: true });
      return newState;
    // case 'toggleCaseSelectedAtIndex':
    // newState = modifyCaseByIndexWithProps(state, action.index)
    default:
      Sentry.captureEvent({
        message: `Error: Reducer (ComparableResultsModule)`,
        extra: {
          err: `Error: action of type ${action.type} is not allowed in reducer`,
          action: action,
        },
      });
      console.error('Error: action of type ', action.type, ' is not allowed in reducer')
      return state;
  }
}

const modifyCaseByIndexWithProps = (state: ModuleStateProps, index: number, props: object): ModuleStateProps => {
  return {
    ...state,
    comparisonCases: state.comparisonCases.map((comparisonCase, comparisonIndex) => {
      if (comparisonIndex !== index) {
        return comparisonCase;
      }
      return {
        ...comparisonCase,
        ...props,
        // data: undefined,
        // isRunning: false,
      } as ComparisonCase
    })
  }
}

export const deleteSavedCaseIds = (caseIds: number[]) => {
  return Promise.all([
    db.savedCases.bulkDelete(caseIds),
    db.savedCaseData.where('savedCaseId').anyOf(caseIds).delete(),
    removeCaseIdsFromBatchesThatIncludeThem({ caseIds: caseIds }),
  ])
}

export const setSavedItemNameById = (id: number, name: string, collectionName: DatabaseCollectionName) => {
  if (id > -1 && !!name) {
    db[collectionName].update(id, { name: name })
    // db.savedCases.update(id, {name: name});
  }
}

const promptUniqueCaseNameForModule = async (moduleType: string | undefined, isRedo?: boolean): Promise<string | null> => {
  if (!moduleType) {
    return null;
  }
  let name = prompt(isRedo ? 'That name already exists in this module. Please choose another:' : 'Choose a name:');
  if (!name) {
    return null;
  }
  const matchingCase = await db.savedCases.filter(c => c.name === name && c.type === moduleType && !c.isDemo).toArray();
  // console.log(matchingCase)
  const doesNameExistAlready = matchingCase?.length;
  // console.log(doesNameExistAlready)
  if (doesNameExistAlready) {
    name = await promptUniqueCaseNameForModule(moduleType, true);
    return name;
  } else {
    return name;
  }
}

/**
 * Returns a promise
 */
const removeCaseIdsFromBatchesThatIncludeThem = ({
  caseIds,
}: {
  caseIds: number[];
}) => {
  return db.savedBatches
    .filter((batch: ComparisonCaseBatch) => {
      return (
        caseIds.some(id => batch.caseIds.includes(id))
      )
    }).modify((value, ref) => { // (value, ref) is a weird Dexie syntax - value refers to the batch, and ref is a pointer to "this" for deleting the whole object
      // This callback is run for every match.
      const newCaseIds = value.caseIds.filter((id: number) => !caseIds.includes(id));
      // if all of this batch's caseIds are in the caseIds we're deleting, then we should just delete the batch, otherwise update the batch w/new filtered case ids
      if (newCaseIds.length === 0) {
        delete ref.value;
      } else {
        value.caseIds = newCaseIds;
      }
    });
}

export const saveCaseAtIndex = async ({
  name,
  index,
  comparisonCases,
  data,
  moduleType,
  subModuleType,
  dispatch,
}: {
  name: string;
  index: number | undefined;
  comparisonCases: ComparisonCase[];
  data: {
    inputStates: Record<string, InputState>;
    customData?: any;
    moduleVersion: number;
  };
  moduleType: string;
  subModuleType?: string;
  dispatch: React.Dispatch<ModuleActionProps> | undefined;
}): Promise<number> => {

  if (typeof index !== 'number' || typeof dispatch !== 'function') {
    throw new Error('Can\'t save case because either index or dispatch was not provided')
  }
  if (!moduleType) {
    throw new Error('Module type not provided to saveCaseAtIndex function');
  }

  const comparisonCase = comparisonCases[index]
  const analysisResult = comparisonCase?.data?.analysisResult;
  const inputStates = data.inputStates;
  const customData = data.customData;
  const moduleVersion = data.moduleVersion;
  const caseId = comparisonCases?.[index]?.id;
  const inputValues = inputStates ? getInputValuesRecordFromInputStates(inputStates) : {};

  const newSavedCase: any = {
    type: moduleType,
    name: name,
    // id: caseId,
    createdAt: new Date(),
  }

  if (subModuleType) {
    newSavedCase.subModuleType = subModuleType
  }

  const savedCaseId = await db.savedCases.put(newSavedCase) as number;

  const savedCaseData: SavedCaseData = {
    savedCaseId,
    analysisResult,
    inputValues,
    customData,
    moduleVersion,
  }

  db.savedCaseData.add(savedCaseData as SavedCaseData).then((savedCaseDataId) => {
    dispatch && dispatch({
      type: 'setComparisonCaseAtIndex',
      value: {
        ...comparisonCase,
        id: caseId,
        savedCaseId: savedCaseId,
        isUnsaved: false,
        name,
        data: savedCaseData,
      },
      index
    });
    // return savedCaseId;
    // console.log('Saved run data stored!')
  }).catch(error => {
    console.log(error);
    // TODO log a sentry error also
  })
  // }).catch(error => {
  //   console.log(error);
  //   // TODO log a sentry error also
  // });

  return savedCaseId;
}

export const saveBatch = ({
  moduleType,
  subModuleType,
  comparisonCases,
  unsavedCaseData,
  dispatch,
}: {
  moduleType: string;
  subModuleType?: string;
  comparisonCases: ComparisonCase[];
  unsavedCaseData?: Array<{
    inputStates?: Record<string, InputState>;
    customData?: any;
  } | undefined>;
  dispatch?: React.Dispatch<ModuleActionProps>;
}) => {

  promptUniqueBatchNameForModule(moduleType).then(batchName => {
    if (batchName) {
      // save any cases that aren't saved yet
      const numUnsavedCases = comparisonCases.filter(c => {
        const isUnsaved = c.isUnsaved || typeof c.savedCaseId !== 'number';
        return isUnsaved;
      })?.length || 0;
      // get multiple valid auto-incremented case names (might need zero of these, if all cases are saved already)
      getUniqueIncrementedCaseNamesForModule({
        startingName: batchName,
        moduleType: moduleType,
        subModuleType,
        numCases: numUnsavedCases,
      }).then(async (incrementedCaseNames) => {
        // need to save all unsaved cases, and get their resulting saved case IDs (to save w/batch)
        const promises: Promise<number>[] = [];
        comparisonCases.forEach((comparisonCase, comparisonIndex) => {
          const isUnsaved = typeof comparisonCase.savedCaseId !== 'number';
          if (isUnsaved) {
            // save case, popping one of the incremetedCaseNames to use
            const caseName = incrementedCaseNames.shift();
            if (!unsavedCaseData?.[comparisonIndex]?.inputStates && !unsavedCaseData?.[comparisonIndex]?.customData) {
              throw new Error('No input states or custom data provided for one or more unsaved cases when saving batch')
            }
            promises.push(saveCaseAtIndex({
              name: caseName || '',
              index: comparisonIndex,
              comparisonCases,
              data: unsavedCaseData[comparisonIndex],
              moduleType: moduleType,
              subModuleType,
              dispatch,
            }))
            // return caseId;
          } else {
            // push dummy promise to just return the already-existing saved case ID, if the case is already saved, for the Promises.all call below - this way we preserve order and make sure all unsaved + saved cases get into the batch
            promises.push(new Promise<number>((resolve, reject) => {
              resolve(comparisonCase.savedCaseId as number)
            }));
          }
        });

        Promise.all(promises).then(savedCaseIds => {
          const newBatch = {
            caseIds: savedCaseIds,
            name: batchName,
            type: moduleType,
            createdAt: new Date(),
          } as ComparisonCaseBatch;
          db.savedBatches.add(newBatch).then(id => {
            if (dispatch) {
              dispatch({
                type: 'setBatch',
                value: {
                  ...newBatch,
                  id
                }
              })
            }
          }).catch(err => {
            console.log(err);
            Sentry.captureEvent({
              message: `Error saving batch`,
              extra: {
                err: JSON.stringify(err),
              },
            });
          });
        }).catch(err => {
          console.log(err);
          Sentry.captureEvent({
            message: `Error resolving promises to save auto-incremented unsaved cases when saving batch`,
            extra: {
              err: JSON.stringify(err),
            },
          });
        });
      }).catch(err => {
        console.log(err);
        Sentry.captureEvent({
          message: `Error in getUniqueIncrementedCaseNamesForModule`,
          extra: {
            err: JSON.stringify(err),
          },
        });
      });
    }
  })
}

export const useRunCaseAtIndex = () => {

  const { client } = useClient()

  const runCaseAtIndex = async ({
    comparisonIndex,
    comparisonCase,
    apiEndpoint,
    inputStates,
    // customBody,
    customRequests,
    customData,
    isValid,
    setError,
    dispatch,
  }: {
    comparisonIndex: number;
    comparisonCase: ComparisonCase | null | undefined;
    apiEndpoint?: string;
    inputStates?: Record<string, InputState>;
    // customBody?: any;
    customRequests?: APIRequestWithType[];
    customData?: unknown;
    isValid: boolean;
    setError: React.Dispatch<React.SetStateAction<string>>;
    dispatch: React.Dispatch<ModuleActionProps>;
  }) => {
    if (!isValid) {
      customAlert({ message: 'There are one or more invalid inputs that need to be corrected before running' })
      return;
    }

    const isCaseAlreadyRun = !!comparisonCase?.data?.analysisResult;
    if (isCaseAlreadyRun) {
      return null;
    }

    // set case to loading
    dispatch({ type: 'setCaseToRunningAtIndex', index: comparisonIndex });
    let body: Record<string, any> = {};
    let requests: APIRequest[] = [];
    const promises: Promise<Record<string, unknown> | undefined>[] = [];
    if (!customRequests && !apiEndpoint) {
      // Sentry.captureEvent({
      //   message: `Error: ${}`,
      //   extra: {
      //     err: JSON.stringify(err),
      //     pathway: JSON.stringify(formattedPathways),
      //   },
      // });
      throw new Error('runCaseAtIndex must receive either customRequests or apiEndpoint, but got neither.')
    }
    if (customRequests) {
      requests = customRequests;
      // body = customBody;
    }
    else if (apiEndpoint) {
      for (let name in inputStates) {
        body[name] = inputStates[name].value;
      }
      requests = [{
        endpoint: apiEndpoint,
        body,
      }];
    } else {
      // fallthrough case - this should never happen - either customRequests or apiEndpoint must be defined
    }
    requests.forEach(request => {
      promises.push(
        client(request.endpoint, {
          body: request.body
        })
      );
    });
    try {
      setError("");
      console.log('trying...');
      const startTime = new Date().getTime();
      const responses = await Promise.all(promises).catch((e) => {
        console.log(e);
        const error = e.error || (e.message.indexOf('Unexpected token') > -1 ? 'There was an error running this analysis. We have logged the error automatically and will fix it as soon as we can.' : e.message);
        // dispatch({type: 'setErrorAtIndex', index: comparisonIndex, value: error});
        setError(error);
        dispatch({ type: 'stopRunningCaseAtIndex', index: comparisonIndex });
      });
      // console.log(responses);
      if (responses && responses.length > 0) {
        const endTime = new Date().getTime();
        console.log(`Analysis took %c ${((endTime - startTime) / 1000).toFixed(1)} seconds `, 'font-weight: bold; background: #0c0; color: white;')
        let analysisResult: Record<string, unknown> = {};
        if (customRequests) {
          customRequests.forEach((request, index) => {
            analysisResult[request.type] = responses[index];
          });
        } else {
          analysisResult = responses[0];
        }
        dispatch({
          type: 'setComparisonCaseAtIndex',
          index: comparisonIndex,
          value: {
            ...comparisonCase,
            id: comparisonCase?.id || generateUniqueIntId(),
            isUnsaved: true,
            data: {
              analysisResult,
              inputValues: !customRequests ? getInputValuesRecordFromInputStates(inputStates) : null,
              customData,
            }
          }
        });
      }
      trigger('afterRunCase');
    } catch (err) {
      console.log('error!', err);
      setError(err.message);
    }
  }

  return runCaseAtIndex;
}



export const ComparableResultsModule: React.FC<{
  moduleData: ComparableResultsModuleProps
}> = ({
  moduleData,
  children,
}): JSX.Element => {

  const initialState: ModuleStateProps = {
    isAnyColumnFullscreened: false,
    numChartCols: 1,
    comparisonCases: [getEmptyComparisonCase()],
    isComparisonMode: false,
    isFocusLinkActive: true,
    allowComparisons: moduleData.allowComparisons,
    allowCaseDuplication: moduleData.allowCaseDuplication || false,
    maxComparisonCases: moduleData.maxComparisonCases || maxComparisonResultCols,
    showRunAllButton: moduleData.showRunAllButton || false,
    allowChartTiling: moduleData.allowChartTiling,
    headerTitle: moduleData.title || getHeaderTitle(location?.pathname || ""),
    apiPath: moduleData.apiPath,
    chartControlAllocation: 'group',
    type: moduleData.type,
    subModuleType: undefined,
  }

  interface ComparisonResultActionValue {
    id: number | null;
    index: number;
  }

  const [state, dispatch] = React.useReducer(reducer, initialState);

  const performQueryStringActions = () => {
    const queryString = location.search?.replace('?', '');
    if (queryString) {
      const [action, value] = queryString.split('=');
      if (typeof action === 'undefined' || typeof value === 'undefined') {
        return;
      }
      let ids;
      switch (action) {
        case 'loadCaseIds':
          ids = value.split(',');
          ids.forEach((id, index) => {
            if (index > 0) {
              dispatch({type: 'addComparisonCol'})
            }
            dispatch({type: 'setComparisonCaseIdAtIndex', value: parseInt(id), index, dispatch});
          })
          break;
        case 'loadBatchId':
          dispatch({type: 'loadBatchId', value: parseInt(value), dispatch});
          break;
        // case 'duplicateCaseId':
        //   dispatch({type: 'loadCaseIdAsDuplicateAtIndex', value, index: 0, dispatch});
        //   break;
        case 'duplicateCaseIds':
          ids = value.split(',');
          ids.forEach((id, index) => {
            if (index > 0) {
              dispatch({type: 'addComparisonCol'})
            }
            dispatch({type: 'loadCaseIdAsDuplicateAtIndex', value: id, index, dispatch});
          })
          break;
        default:
          break;
      }
      var cleanURI = location.protocol + "//" + location.host + location.pathname;
      window.history.replaceState({}, document.title, cleanURI);
    }
  }

  React.useEffect(() => {
    performQueryStringActions()
  }, [])

  const isFocusLinkingDisabled = useAtomValue(isFocusLinkingDisabledAtom)

  // sync isFocusLinkActive state with isFocusLinkingDisabled atom (which will only ever be true if different paths are loaded in Paths module)
  React.useEffect(() => {
    if (isFocusLinkingDisabled && state.isFocusLinkActive) {
      dispatch({type: 'setIsFocusLinkActive', value: false})
    } else if (!isFocusLinkingDisabled && !state.isFocusLinkActive) {
      dispatch({type: 'setIsFocusLinkActive', value: true})
    }
  }, [isFocusLinkingDisabled])

  // if (process.env.NODE_ENV === 'development') {
  //   console.log(JSON.stringify(state.comparisonCases))
  // }

  return (
    <ModuleStateContext.Provider value={state}>
      <ModuleDispatchContext.Provider value={dispatch}>
        <SEO title={state.headerTitle || ''} />
        {children}
      </ModuleDispatchContext.Provider>
    </ModuleStateContext.Provider>
  )
}

export const ComparisonRow = ({
  sidebar,
  content,
  className,
  style,
  columnizeContent = true,
}:  {
  sidebar?: JSX.Element,
  content?: JSX.Element[],
  className?: string,
  style?: React.CSSProperties,
  columnizeContent?: boolean,
}) => {
  const { isComparisonMode, comparisonCases } = React.useContext(ModuleStateContext);
  const numCols = columnizeContent ? (comparisonCases?.length || 1) : 1;
  return (
    <div
      className={`${isComparisonMode ? 'flex' : 'gutter-x'} ${className ? className : ''}`}
      style={style}
    >
      {isComparisonMode && sidebar &&
        <div className={isComparisonMode ? 'comparison-sidebar' : ''}>
          {sidebar}
        </div>
      }
      <div
        className={`${isComparisonMode ? 'comparison-main' : ''} ${!sidebar && 'ml-[-1px]'}`}
        style={{gridTemplateColumns: `repeat(${content?.length}, minmax(0, 1fr))`}}
      >
        {content}
      </div>
    </div>
  )
}
