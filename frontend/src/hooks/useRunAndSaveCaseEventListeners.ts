import { useEventListener } from "./useEventListener";

export const useRunAndSaveCaseEventListeners = (
  runCase: () => void,
  saveCase: () => void,
  comparisonIndex: number,
  handleDuplicate?: () => void,
) => {

  const saveAnalysisResult = (e: CustomEvent) => {
    if (e.detail.comparisonIndex === comparisonIndex) {
      saveCase();
    }
  }
  
  const runAnalysis = (e: CustomEvent) => {
    if (e.detail.comparisonIndex === comparisonIndex) {
      runCase();
    }
  }

  const runAllAnalyses = (e: CustomEvent) => {
    runCase();
  }

  const duplicateCase = (e: CustomEvent) => {
    if (e.detail.comparisonIndex === comparisonIndex) {
      if (typeof handleDuplicate !== 'undefined') {
        handleDuplicate();
      } else {
        throw new Error('Cannot duplicate case, because there was no handleDuplicate function provided to useRunAndSaveCaseEventListeners');
      }
    }
  }

  useEventListener('saveAnalysisResult', saveAnalysisResult)
  useEventListener('runCase', runAnalysis);
  useEventListener('runAllAnalyses', runAllAnalyses);
  useEventListener('duplicateCase', duplicateCase);
}

