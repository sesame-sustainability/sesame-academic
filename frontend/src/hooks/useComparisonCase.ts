import * as React from "react"
import { ModuleStateContext } from "../components/comparableResultsModule"

export const useComparisonCase = (comparisonIndex: number): ComparisonCase | null | undefined => {
  const { comparisonCases } = React.useContext(ModuleStateContext)
  return comparisonCases?.[comparisonIndex]
}