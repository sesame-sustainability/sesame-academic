import { atom } from "jotai"

// export const pathsInputHandlersAtom = atom<UnifiedLCATEAComparisonCaseInputHandler[]>([])

export const pathsByCaseIdAtom = atom<{
  nodesChosen: Array<string | null>,
  caseId: number,
}[]>([])

/**
 * This atom tracks whether the focus link button should be disabled.
 * As of this writing, that only happens when we're in Paths builder,
 * and there are comparison cases active that have different paths.
 */
export const isFocusLinkingDisabledAtom = atom(
  (get) => {
    let isDisabled = false
    const pathNodesByCase = get(pathsByCaseIdAtom)
      .map(pathsObj => pathsObj.nodesChosen)
      .filter(pathNodes => !!pathNodes)
    
    if (pathNodesByCase?.length > 0) {
      const stringifiedPathNodesByCase = pathNodesByCase.map(nodes => JSON.stringify(nodes))
      const areAllCasePathsTheSame = (new Set(stringifiedPathNodesByCase).size === 1)
      if (!areAllCasePathsTheSame) {
        isDisabled = true
      }
    }    
    return isDisabled
  }
)