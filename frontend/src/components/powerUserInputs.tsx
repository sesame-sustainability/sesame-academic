import React, { useEffect, useMemo, useState } from "react";
import * as Styles from "./styles";
import { CategoricalSelect } from "./appSelects";
import Accordion from "./accordion";
import { generateUniqueIntId, groupUserInputs } from "../utils";
import useClient from "../hooks/useClient";
import useAppMetadata from "../hooks/useAppMetadata";
import useUserInputs, { getInputValuesRecordFromInputStates } from "../hooks/useUserInputs";
import { Dataset } from "./figures";
import { Cell, useTable, Table, TableInputs } from "./tables";
import { useContext } from "react";
import { ModuleDispatchContext, ModuleStateContext, useRunCaseAtIndex } from "./comparableResultsModule";
import { useRunAndSaveCaseEventListeners } from "../hooks/useRunAndSaveCaseEventListeners";
import { db } from "../hooks/useDB";
import UserInputs from "./userInputs";
import { useSettingValue } from "../hooks/useSettings";
import { useMakeSureSomeInputsAreVisibleAtIndex } from "../hooks/useMakeSureSomeInputsAreVisibleAtIndex";

type InputGroup = {
  title?: string;
  userInputs: UserInputProperties[];
};

type AnalysisResult = {
  figures: {
    demand: AnalysisResultFigure;
    generation_stacked: AnalysisResultFigure;
    generation_line: AnalysisResultFigure;
    multi: Dataset[];
  };
};

type AnalysisResultFigure = {
  title: string;
  type: string;
  datasets: Dataset[];
};

type SavedAnalysisResult = Record<
  string,
  {
    analysisResult: AnalysisResult;
    inputStates: Record<string, InputState>[];
    createdAt: Date;
    label: string;
    userInputs: UserInputProperties[];
  }
>

export const PowerUserInputsHandler = ({
  comparisonIndex,
}: {
  comparisonIndex: number,
}) => {

  const { client } = useClient();
  const {
    grid: { grid: gridMetadata },
  } = useAppMetadata();

  const dispatch = useContext(ModuleDispatchContext);
  const { comparisonCases, type } = useContext(ModuleStateContext);
  const moduleType = type;
  const comparisonCase = comparisonCases ? comparisonCases[comparisonIndex] : null;
  const analysisResult = comparisonCases ? comparisonCases[comparisonIndex]?.data?.analysisResult : null;
  const caseId = comparisonCases?.[comparisonIndex]?.id;

  const [inputs, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(gridMetadata.user_inputs, undefined, undefined, comparisonCase?.data?.inputValues);
  const [error, setError] = useState<string>('');

  const runCaseAtIndex = useRunCaseAtIndex()

  const handleRun = () => {
    runCaseAtIndex({
      comparisonIndex,
      comparisonCase,
      apiEndpoint: '/grid/analysis',
      inputStates: inputs,
      isValid: isValid && !error,
      setError: setError,
      dispatch: dispatch,
    })
  }

  const handleSave = () => {
    dispatch({
      type: 'saveCaseAtIndex',
      index: comparisonIndex,
      value: {
        inputStates: inputs, // we have to send inputStates here b/c they aren't tracked in moduleState yet, only in each module itself. 
      },
      dispatch: dispatch // have to send this b/c we have to call dispatch asynchronously from inside comparableResultsModule > reducer, but it doesn't have access to dispatch by itself
    })
  }

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
    inputStates: inputs
  })

  useRunAndSaveCaseEventListeners(handleRun, handleSave, comparisonIndex)

  return (
    <div>
      <UserInputs
        userInputs={gridMetadata.user_inputs}
        comparisonIndex={0}
        inputStates={inputs}
        inputGroupOpenStates={inputGroupOpenStates}
        toggleInputGroupOpenState={toggleInputGroupOpenState}
        setInput={setInput}
        setInputError={setInputError}
      />
      {error && (
        <div className="text-red-700">
          <br />
          {error}
        </div>
      )}
    </div>
  )
}