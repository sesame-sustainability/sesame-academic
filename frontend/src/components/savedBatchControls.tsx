import * as React from "react"
import { trigger } from "../utils/events";
import { ModuleDispatchContext, ModuleStateContext } from "./comparableResultsModule";
import { SavedItemMenu } from "./savedItemMenu";
import { Button } from "./styles";

export const SavedBatchControls = () => {

  const { comparisonCases, savedBatch, type } = React.useContext(ModuleStateContext);
  const dispatch = React.useContext(ModuleDispatchContext);

  const numCasesWithResults = comparisonCases?.filter(c => !!c.data?.analysisResult)?.length || 0;
  const isBatchSaveButtonDisabled = (
    !!savedBatch
    ||
    numCasesWithResults <= 1
  )
  let batchSaveButtonTooltip = '';
  if (!!savedBatch) {
    batchSaveButtonTooltip = 'Batch already loaded';
  } else if (numCasesWithResults <= 1) {
    batchSaveButtonTooltip = 'Must have at least 2 cases with results to save a batch'
  }

  return (
    <div className="flex flex-col items-start my-4 space-y-2">
      <SavedItemMenu
        collectionName="savedBatches"
        layout="column"
        itemTitle="Batch"
        comparisonIndex={0}
        activeItem={savedBatch}
        activeItemId={savedBatch?.id}
        activeItemName={savedBatch?.name}
      />
      <Button
        size="small"
        disabled={isBatchSaveButtonDisabled}
        title={batchSaveButtonTooltip}
        id="save-batch"
        onClick={() => {
          if (type) {
            trigger('saveBatch');
            // saveComparisonCaseBatch({
            //   comparisonCases: comparisonCases || [],
            //   moduleType: type,
            //   dispatch,
            // });
          }
        }}
      >
        Save Batch
      </Button>
    </div>
  )
}