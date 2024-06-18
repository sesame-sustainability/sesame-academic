import * as React from "react"
import { getCaseNameFromComparisonCaseAtIndex, ModuleDispatchContext, ModuleStateContext } from "../components/comparableResultsModule"
import { customAlert } from "../components/customAlert"

/**
 * Handle the scenario where focus mode is enabled,
 * but all focused inputs are hidden,
 * leaving no visible inputs at all.
 * If so, disable focus mode and clear focusedInputs state
 */
export const useMakeSureSomeInputsAreVisibleAtIndex = ({
  comparisonIndex,
  inputStates,
  getCustomAreAnyInputsVisible,
}: {
  comparisonIndex: number
} & ( // must have one or the other of these two properties, but not both
  | { inputStates: Record<string, InputState>, getCustomAreAnyInputsVisible?: never }
  | { inputStates?: never, getCustomAreAnyInputsVisible: () => boolean }
)) => {

  const dispatch = React.useContext(ModuleDispatchContext)
  const { comparisonCases, isFocusLinkActive } = React.useContext(ModuleStateContext)
  const comparisonCase = comparisonCases?.[comparisonIndex]
  const isFocusModeActive = comparisonCase?.isFocusModeActive
  if (!comparisonCase) return null
  const focusedInputs = comparisonCase.focusedInputs
  if (typeof inputStates === 'undefined' && typeof getCustomAreAnyInputsVisible === 'undefined') {
    throw new Error('Error: must provide either inputStates or customAreAnyInputsVisible, but both are undefined')
  }

  React.useEffect(() => {
    if (isFocusModeActive) {
      let areAnyInputsVisible = false;

      if (typeof getCustomAreAnyInputsVisible !== 'undefined') {
        areAnyInputsVisible = getCustomAreAnyInputsVisible()
      } else {
        const inputKeys = Object.keys(inputStates || {});
        if (inputStates) {
          areAnyInputsVisible = inputStates && inputKeys.some(key => focusedInputs?.includes(key) && inputStates[key].isVisible)
        }
      }
      const areNoFocusedInputs = !focusedInputs || focusedInputs.length === 0;
      if (areNoFocusedInputs || !areAnyInputsVisible) {

        let message = ''
        // if link mode is active, disable focus across all cases, or just break focus link... which?
        if (isFocusLinkActive) {
          dispatch({type: 'disableFocusModeForAllCases'});
          message = `Focus mode automatically disabled, because one or more cases had no visible inputs.`
        } else {
          dispatch({type: 'toggleFocusModeAtIndex', index: comparisonIndex});
          message = `Focus mode automatically disabled for ${getCaseNameFromComparisonCaseAtIndex(comparisonCase, comparisonIndex)} because all inputs were hidden.`
        }
        customAlert({ type: 'info', message })
      }
    }
  }, [isFocusModeActive, focusedInputs, getCustomAreAnyInputsVisible])  
}