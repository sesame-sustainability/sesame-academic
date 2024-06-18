import * as React from "react"
import { dispatch } from "react-hot-toast/dist/core/store";
import { deleteSavedCaseIds, ModuleDispatchContext } from "../components/comparableResultsModule";
import { customAlert } from "../components/customAlert";
import { useComparisonCase } from "./useComparisonCase";
import { db } from "./useDB";

/**
 * Invalidate a loaded case if it's stale, i.e. created with an old module version
 */
export const useInvalidateStaleCases = ({
  // comparisonCase,
  moduleMetadata,
  comparisonIndex,
  customIsCaseStale,
}: {
  customIsCaseStale?: boolean,
  moduleMetadata?: BasicModuleMetadata,
  comparisonIndex: number,
}) => {
  const dispatch = React.useContext(ModuleDispatchContext)
  const comparisonCase = useComparisonCase(comparisonIndex)
  // console.log(comparisonCase, comparisonIndex)

  const invalidateCase = () => {
    const caseId = comparisonCase?.savedCaseId;
    if (typeof caseId === 'number') {
      invalidateCaseById({
        id: caseId,
        dispatch,
        comparisonIndex
      })
    }
  }

  React.useEffect(() => {
    if (customIsCaseStale) {
      invalidateCase()
    }
  }, [customIsCaseStale])

  // invalidate case if it's from an old module version
  React.useEffect(() => {
    const thisCaseModuleVersion = comparisonCase?.data?.moduleVersion
    const currentModuleVersion = moduleMetadata?.version;
    // don't check for case staleness if the saved case data hasn't loaded into the comparison case yet, because module version will not be present (it's in saved case data)
    if (!comparisonCase?.data) {
      return;
    }
    const isCaseStale = (
      comparisonCase?.savedCaseId
      &&
      thisCaseModuleVersion !== currentModuleVersion
      &&
      !comparisonCase?.isDemo
    )
    if (isCaseStale) debugger
    // console.log(isCaseStale)
    // if (isCaseStale) {
    //   invalidateCase()
    // }
  }, [comparisonCase, moduleMetadata])
}

const invalidateCaseById = ({
  id,
  dispatch,
  comparisonIndex,
}: {
  id: number;
  dispatch: (value: ModuleActionProps) => void;
  comparisonIndex: number,
}) => {

  deleteSavedCaseIds([id]).then(() => {
    dispatch({type: 'clearComparisonCaseAtIndex', index: comparisonIndex})
    customAlert({
      type: 'error',
      message: `This case was created using an outdated version of this module. For data integrity, we've deleted the case. We've attempted to preserve the input values, but some input options may have changed. Please check your inputs and re-run to get up-to-date results.`
    })
  })

  // Promise.all([
  //   // db.savedCases.update(id, {isStale: true}),
  //   // db.savedCaseData.where('savedCaseId').equals(id).modify((obj: SavedCaseData) => {
  //   //   delete obj.analysisResult;
  //   //   obj.isStale = true;
  //   // })
  //   db.savedCases.delete(id),
  //   db.savedCaseData.where('savedCaseId').equals(id).delete(),
  // ]).then(() => {
  // })

  // db.savedCaseData.update(id, {
  //   analysisResult: undefined,
  //   isStale: true,
  // }).then(() => {
  //   dispatch({type: 'setComparisonCaseIdAtIndex', value: id, index: comparisonIndex})
  // })
}
