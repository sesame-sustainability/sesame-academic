import React, { useEffect, useMemo } from "react";
import * as Sentry from "@sentry/browser";
import { navigate, Link } from "gatsby";
import { RouteComponentProps } from "@reach/router";
import useQueryString from "use-query-string";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { List, arrayMove } from 'react-movable';

import useLocalStorage from "../../hooks/useLocalStorage";
import useAppMetadata from "../../hooks/useAppMetadata";

import { CustomInputValues, PathwayCreator1Page, PathwayCreatorState, StageInputValues } from "../pathwayCreator1Page"

import useClient from "../../hooks/useClient";
import * as Styles from "../styles";
import { groupByPathway, groupByKeys, capitalStr, groupBy } from "../../utils";
import { dataLackingPercentageVariation, tornadoChartOpts } from "../graphs/TornadoChartOpts";
import PathwayAnalysisGraph from "../pathwayAnalysisGraph";
import Layout from "../layout";
import { teaChartOptions } from "./TEA";
import { ChartExportButton } from "../chartExportButton";
import { Toggle } from "../toggle";
import { TiledColumn } from "../tiledColumn";
import { ComparisonRow, getCaseNameFromComparisonCaseAtIndex, ModuleDispatchContext, ModuleStateContext, saveBatch } from "../comparableResultsModule";
import { Tooltip } from "../tooltip";
import { useEventListener } from "../../hooks/useEventListener";
import { trigger } from "../../utils/events";
import { customAlert } from "../customAlert";
import { SavedBatchControls } from "../savedBatchControls";
import { getInputValuesRecordFromInputStates } from "../../hooks/useUserInputs";
import { isFocusLinkingDisabledAtom, pathsByCaseIdAtom } from "../../store/store";
import { useAtom, useAtomValue } from "jotai";

const getTornadoTitleTooltipWithType = (analysisType: 'emissions' | 'costs') => {
  return `Each bar corresponds to an input on left. The bar shows how much ${analysisType} change from their default value if the input is changed from its default value. See individual bars for change details. Flags next to inputs indicate that SESAME currently lacks the data needed to estimate the 20th & 80th percentile values of the flagged input. Instead, the input is varied by plus & minus ${dataLackingPercentageVariation}% from its default value.`
}

const TornadoChart = ({ chart }) => {
  return (
    <>
      {chart?.show && (
        <div className="mt-6 mb-3 relative" style={{breakInside: "avoid"}}>
          {/* <Styles.ChartTitle>
            {chart.opts?.title}
            {chart.opts?.titleTooltipContent &&
              <Tooltip data={{content: chart.opts?.titleTooltipContent}}/>
            }
          </Styles.ChartTitle> */}
          <HighchartsReact
            ref={chart.ref}
            highcharts={Highcharts}
            options={chart.opts}
          />
        </div> 
      )}
    </>
  )
};

const ReorderableChartGridRow = ({
  blocks,
  isTwoColLayout,
}: {
  blocks: JSX.Element[];
  isTwoColLayout: boolean;
}) => {

  return (
    <div className={`grid ${isTwoColLayout ? 'grid-cols-2 divide-x' : 'grid-cols-1 divide-y'}`}>
      {blocks.map(block => (
        <div className={`gutter-x`}>
          {block}
        </div>
      ))}
    </div>
  )
}

export const ReorderableChartGrid = ({
  oneColumnOrder,
  twoColumnOrder,
  blocks,
  header,
  showHeader,
}: {
  oneColumnOrder: number[];
  twoColumnOrder: number[];
  blocks: JSX.Element[];
  header?: JSX.Element;
  showHeader?: boolean;
}) => {
  const { isComparisonMode, isAnyColumnFullscreened } = React.useContext(ModuleStateContext)
  const isTwoColLayout = isComparisonMode || isAnyColumnFullscreened || false;
  const currentOrder = isTwoColLayout ? twoColumnOrder : oneColumnOrder
  const sortedBlocks = currentOrder.map(index => blocks[index])
  const numRows = sortedBlocks.length / 2

  return (
    <div className="divide-y">
      {showHeader && header}
      {new Array(numRows).fill(null).map((o, rowIndex) => (
        <ReorderableChartGridRow
          blocks={[sortedBlocks[rowIndex * 2], sortedBlocks[rowIndex * 2 + 1]]}
          isTwoColLayout={isTwoColLayout}
        />
      ))}
    </div>
  )
}

const ProductChartGroup = ({
  charts,
  isTwoColChartLayout,
  numChartGroups,
}: {
  charts: any;
  isTwoColChartLayout: boolean;
  numChartGroups: number;
}) => {
  const {product, lcaChart, lcaTornados, teaResponses, teaTornados, pathways} = charts;
  
  const [isTeaChartStacked, setIsTeaChartStacked] = React.useState(true);
  const [selectedLCATornadoIndex, setSelectedLCATornadoIndex] = React.useState<number>(0);
  const [selectedTEATornadoIndex, setSelectedTEATornadoIndex] = React.useState<number>(0);

  const [selectedTornadoPathwayIndex, setSelectedTornadoPathwayIndex] = React.useState<number>(0);

  const selectedTornadoPathway = pathways?.[selectedTornadoPathwayIndex];

  const selectedLCATornado = lcaTornados?.find(tornado => (
    tornado.productType === selectedTornadoPathway?.productType
    &&
    tornado.resource === selectedTornadoPathway?.resource
  ))
  const selectedTEATornado = teaTornados?.find(tornado => (
    tornado.productType === selectedTornadoPathway?.productType
    &&
    tornado.resource === selectedTornadoPathway?.resource
  ));

  const teaChartRef = React.useRef();
  const lcaTornadoRef = React.useRef();
  const teaTornadoRef = React.useRef();

  if (selectedLCATornado) {
    selectedLCATornado.ref = lcaTornadoRef;
  }
  if (selectedTEATornado) {
    selectedTEATornado.ref = teaTornadoRef;
  }

  const lcaChartElement = (
    <>
      {lcaChart &&
        <PathwayAnalysisGraph
          response={lcaChart}
        />
      }
    </>
  )
  
  const getPathwayName = (pathway): string => {
    if (!pathway) {
      return null;
    }
    return `${pathway.productType} from ${pathway.resource}`
  }

  const tornadoPathwayChooser = (
    <Styles.Select
      value={selectedTornadoPathwayIndex}
      className="!w-auto"
      onChange={(e) => {
        const newIndex = parseInt(e.target.value);
        setSelectedTornadoPathwayIndex(newIndex);
      }}
    >
      <option value={-1} label='' />
      {pathways.map((pathway, index) => (
        <option value={index} label={getPathwayName(pathway)} />
      ))}
    </Styles.Select>
  );

  const lcaTornadoElement = (
    <>
      {lcaTornados?.length > 0 &&
        <div className="mb-4">
          <div className="flex flex-row items-center justify-center pt-4 relative">
            <Styles.ChartTitle className="flex-shrink-0 flex-initial !my-0 mr-3">Emissions Sensitivity for:</Styles.ChartTitle>
            {tornadoPathwayChooser}
            {selectedLCATornado?.opts?.titleTooltipContent &&
              <Tooltip data={{content: selectedLCATornado.opts?.titleTooltipContent}}/>
            }
            <div className="mt-2">
              <ChartExportButton className="top-[0.9rem]" chartTitle={`Emissions Sensitivity for ${getPathwayName(selectedTornadoPathway)}`} chartRef={lcaTornadoRef} />
            </div>
          </div>
          {selectedLCATornado && 
            <TornadoChart chart={selectedLCATornado} />
          }
        </div>
      }
    </>
  )
  
  const teaChartElement = (
    <>
      {teaResponses &&
        <div className="relative">
          <Styles.ChartTitle>Costs</Styles.ChartTitle>
          <HighchartsReact
            ref={teaChartRef}
            highcharts={Highcharts}
            options={teaChartOptions({
              teaData: teaResponses,
              // categories: [teaName],
              categories: teaResponses.map(teaResponse => teaResponse.title),
              isChartStacked: isTeaChartStacked,
            })}
          />
          <div className="absolute top-6 left-0">
            <Toggle label="Stack Bars" value={isTeaChartStacked} setValue={setIsTeaChartStacked} />
          </div>
          <ChartExportButton chartRef={teaChartRef} chartTitle={`Costs: ${product}`} />
        </div>
      }
    </>
  );

  const teaTornadoElement = (
    <>
      {teaTornados?.length > 0 &&
        <div className="mb-4">
          <div className="flex flex-row items-center justify-center pt-4 relative">
            <Styles.ChartTitle className="flex-shrink-0 flex-initial !my-0 mr-3">Costs Sensitivity for:</Styles.ChartTitle>
            {tornadoPathwayChooser}
            {selectedTEATornado?.opts?.titleTooltipContent &&
              <Tooltip data={{content: selectedTEATornado.opts?.titleTooltipContent}}/>
            }
            {selectedTEATornado &&
              <ChartExportButton className="top-[0.9rem]" chartTitle={`Costs Sensitivity for ${getPathwayName(selectedTornadoPathway)}`} chartRef={teaTornadoRef} />
            }
          </div>

          {selectedTEATornado && 
            <TornadoChart chart={selectedTEATornado} />
          }
        </div>
      }
    </>
  )
  
  const shouldShowProductHeaders = numChartGroups > 1;
                
  return (
    <ReorderableChartGrid
      key={product}
      oneColumnOrder={[0,1,2,3]}
      twoColumnOrder={[0,2,1,3]}
      showHeader={shouldShowProductHeaders}
      header={
        <div className="text-lg h-12 flex items-center justify-center text-gray-500 text-center bg-gray-100">
          Product:&nbsp;<span className="font-bold text-gray-700">{product}</span>
        </div>
      }
      blocks={[lcaChartElement, lcaTornadoElement, teaChartElement, teaTornadoElement]}
    />
    
  )
}

export const getInputValuesByStage = ({
  stages,
  arrayOfStageInputHandlers,
  nodesChosen,
}: {
  stages: any[];
  arrayOfStageInputHandlers: InputHandler[];
  nodesChosen: Array<string | null>;
}): StageInputValues[] => {
  return stages.map((stage, index) => {
    const stageInputHandler = arrayOfStageInputHandlers[index];
    const inputStates = stageInputHandler.inputStates;
    return {
      nodeChosen: nodesChosen[index],
      inputValues: inputStates ? getInputValuesRecordFromInputStates(inputStates) : {},
    }
  }) as StageInputValues[];
}

type DataSourceVersion = {id: string; version: number}

export const getCurrentDataSourceVersions = ({
  stages,
}: {
  stages: Stage[];
}) =>  {
  const allDataSourceVersions: Array<DataSourceVersion | undefined> = stages.map(stage => {
    const sources = stage?.activities?.map(activity => activity.sources).flat();
    return sources?.map(source => ({id: source.id, version: source.version})).flat()
  }).flat()
  return allDataSourceVersions;
}

export const getDataSourceVersion = ({
  dataSourceId,
  allDataSourceVersions,
}: {
  dataSourceId: string | null;
  allDataSourceVersions: Array<DataSourceVersion | undefined>;
}) => {
  return allDataSourceVersions.find(dataSourceVersion => dataSourceVersion?.id === dataSourceId)?.version ?? null
}

export const getCustomInputValues = ({
  inputHandler,
  stages,
}: {
  inputHandler: UnifiedLCATEAComparisonCaseInputHandler;
  stages: Stage[];
}): CustomInputValues => {

  const pathwayCreatorState = inputHandler.pathwayCreatorState;
  const allDataSourceVersions = getCurrentDataSourceVersions({stages});
  const dataSourceVersionsChosen = pathwayCreatorState.dataSourcesChosen.map(dataSourceId => getDataSourceVersion({dataSourceId, allDataSourceVersions}))

  return {
    startWith: pathwayCreatorState.startWith,
    selectedProduct: pathwayCreatorState.selectedProduct,
    selectedProductType: pathwayCreatorState.selectedProductType,
    selectedResource: pathwayCreatorState.selectedResource,
    additionalBackendInputValues: inputHandler.additionalBackendInputValues,
    dataSourcesChosen: pathwayCreatorState.dataSourcesChosen,
    dataSourceVersions: dataSourceVersionsChosen,
  }; 
}

export const UnifiedLCATEA = (): JSX.Element => {

  const { isAnyColumnFullscreened, comparisonCases, maxComparisonCases, isComparisonMode, type } = React.useContext(ModuleStateContext) as ModuleStateProps;
  const dispatch = React.useContext(ModuleDispatchContext);

  const {
    allStage: { edges: allStageNodes },
  } = useAppMetadata();

  const [pathsByCaseId, setPathsByCaseId] = useAtom(pathsByCaseIdAtom)

  React.useEffect(() => {
    // console.log('onMount')
    setPathsByCaseId([])
    return (() => {
      setPathsByCaseId([])
    })
  }, [])

  const stages = React.useMemo(() => {
    // manually set the stage order to avoid bug where cached stage order gets borked somehow, crashing this module
    const stageOrder = ['Upstream','TEA','Midstream','Process','GateToEnduse','Enduse'];
    const stages = new Array(6);
    JSON.parse(JSON.stringify(allStageNodes)).forEach(stageNode => {
      const stageIndex = stageOrder.indexOf(stageNode.node.name);
      stages[stageIndex] = stageNode.node;
    });
    return stages.filter(stage => !!stage);
  }, [allStageNodes])

  const arrayOfComparisonCaseInputHandlers: UnifiedLCATEAComparisonCaseInputHandler[] = new Array(maxComparisonCases).fill(null).map(o => ({
    nodesChosen: [] as string[],
    arrayOfStageInputHandlers: [] as InputHandler[],
    customInputStates: {} as Record<string, string>,
    additionalBackendInputValues: {} as Record<string, boolean>,
    pathwayCreatorState: {} as PathwayCreatorState,
    // setPathwayCreatorState: (() => {}) as React.Dispatch<React.SetStateAction<PathwayCreatorState>>,
  }));

  const analysisResults = React.useMemo(() => {
    return comparisonCases?.map((comparisonCase, comparisonIndex) => {
      let analysisResult = comparisonCase.data?.analysisResult as PathwayAnalysisResponseWithUnformattedData[];
      if (analysisResult) {
        analysisResult = {
          ...analysisResult,
          caseName: comparisonCase.name || getCaseNameFromComparisonCaseAtIndex(comparisonCase, comparisonIndex), // || analysisResult.LCA?.data?.[0]?.[3] || 
          product: comparisonCase.data?.customData?.customInputValues?.selectedProduct,
          productType: comparisonCase.data?.customData?.customInputValues?.selectedProductType,
          resource: comparisonCase.data?.customData?.customInputValues?.selectedResource,
        }
      }
      return analysisResult;
    })
  }, [JSON.stringify(comparisonCases)])

  const analysisResultsWithLCAData = analysisResults?.filter(analysisResult => !!analysisResult?.LCA);
  const analysisResultsBatchedByProduct = analysisResultsWithLCAData ? groupBy(analysisResultsWithLCAData, 'product') : null;

  const chartsGroupedByProduct: any = {};

  // // this block is temporary code to clone solar sensitivity chart to ng power which doesn't have one yet
  // if (analysisResultsBatchedByProduct['Electricity']) {
  //   const sensitivityChartToClone = analysisResultsWithLCAData?.filter(r => r?.LCA?.sensitivity).map(r => r?.LCA?.sensitivity)?.[0];
  //   analysisResultsBatchedByProduct['Electricity'] = analysisResultsBatchedByProduct['Electricity'].map(a => {
  //     if (!a?.LCA?.sensitivity) {
  //       a.LCA.sensitivity = sensitivityChartToClone;
  //     }
  //     return a;
  //   })
  // }

  // build LCA charts
  for (const product in analysisResultsBatchedByProduct) {
    chartsGroupedByProduct[product] = {
      pathways: [] as Array<{productType: string, resource: string}>
    };
    const analysisResultsForThisProduct = analysisResultsBatchedByProduct[product];
    const aggregatedLCADataFromAllCases = analysisResultsForThisProduct?.map(analysisResult => {
      let data = null;
      if (analysisResult.LCA) {
        data = groupByPathway(analysisResult.LCA).data[0];
        data.pathway = analysisResult.caseName; // bring in proper case name
      }
      return data;
    });
    const prototypeAnalysisResult = analysisResultsForThisProduct?.find(analysisResult => !!analysisResult) as {
      LCA: PathwayAnalysisResponseWithUnformattedData,
      TEA?: PathwayAnalysisResponseWithUnformattedData,
    };
    const prototypeAnalysisResultWithAggregatedLCADataFromAllCases = {
      ...prototypeAnalysisResult?.LCA,
      data: aggregatedLCADataFromAllCases,
      title: `${prototypeAnalysisResult?.LCA?.title}`// (${product})`,
    }
    if (prototypeAnalysisResult) {

      const lcaChart = prototypeAnalysisResultWithAggregatedLCADataFromAllCases;
      chartsGroupedByProduct[product].lcaChart = lcaChart;

      // build LCA tornados
    
      const lcaUnit = lcaChart?.unit;

      // const solarTornadoChartOpts = tornadoChartOpts(lcaChart);
      let lcaTornados = [];
      
      analysisResultsBatchedByProduct[product].forEach(analysisResult => {
        
        const { productType, resource } = analysisResult;
        const pathway = { productType, resource };
        const isThisPathwayAddedYet = chartsGroupedByProduct[product].pathways.some(pathway => {
          return pathway.productType === productType && pathway.resource === resource
        });

        const sensitivityChart = analysisResult?.LCA?.sensitivity;
        if (sensitivityChart) {
          const chartOptions = tornadoChartOpts(analysisResult.LCA);
          chartOptions.yAxis[1].title.text = lcaUnit;
          const isThisPathwayTornadoAddedYet = lcaTornados.some(tornado => {
            return (
              tornado.productType === analysisResult.productType
              &&
              tornado.resource === analysisResult.resource
            )
          })
          if (!isThisPathwayTornadoAddedYet) {
            lcaTornados.push({
              show: !!sensitivityChart,
              caseName: analysisResult.caseName,
              productType: analysisResult.productType,
              resource: analysisResult.resource,
              opts: {
                ...chartOptions,
                title: `${chartsGroupedByProduct[product].lcaChart?.title}: Sensitivity`,
                titleTooltipContent: getTornadoTitleTooltipWithType('emissions'),
              },
            });
            if (!isThisPathwayAddedYet) {
              chartsGroupedByProduct[product].pathways.push(pathway);
            }
          }
        }
      })
      
      // lcaTornados = lcaTornados.map(chart => {
      //   return {
      //     ...chart,
      //     ref: React.useRef(null),
      //   }
      // });
      // if (lcaTornados.some(lcaTornado => lcaTornado.show)) {
      chartsGroupedByProduct[product].lcaTornados = lcaTornados;
      // }
      // chartsGroupedByProduct[product].lcaTornados.forEach((tornado, index) => {
      //   chartsGroupedByProduct[product].lcaTornados[index].ref = React.useRef(null);
      // })

      // build TEA bar charts
      const teaResponses = analysisResultsForThisProduct?.map(analysisResult => {

        const teaData = analysisResult?.TEA;
        if (!analysisResult || !teaData) {
          return null;
        }
        let teaResponse = groupByKeys(teaData as PathwayAnalysisResponseWithUnformattedData, [
          "cost_category",
          "cost_category_by_parts",
        ]);
        teaResponse = {
          ...teaResponse,
          title: analysisResult.caseName,
          caseName: analysisResult.caseName,
          productType: analysisResult.productType,
          resource: analysisResult.resource,
        }

        // const data: Data | undefined = prototypeTEAResponse?.data[0];
        // let teaName = '';
        // if (data) {
        //   teaName = data["pathway"].toString();
        // }
        return teaResponse;

      }).filter(teaResponse => !!teaResponse)

      // build TEA tornados
      if (teaResponses.some(teaResponse => !!teaResponse)) {
        chartsGroupedByProduct[product].teaResponses = teaResponses;
        const prototypeTeaResponse = teaResponses[0];
        if (prototypeTeaResponse) {
          const teaTornados = [];
          const teaUnit = prototypeTeaResponse.unit;
          teaResponses.forEach(teaResponse => {
            const { productType, resource, caseName, sensitivity } = teaResponse;
            const teaTornado = {
              show: !!sensitivity,
              caseName,
              productType,
              resource,
              opts: {
                ...tornadoChartOpts(teaResponse, "costs"),
                title: `Costs: Sensitivity`,//`Costs (${product}): Sensitivity`,
                titleTooltipContent: getTornadoTitleTooltipWithType('costs'),
              },
              // ref: React.useRef(null),
            };
            const hasThisProductTypeResourcePairTornadoAlreadyBeenAdded = teaTornados.some(tornado => {
              return (
                tornado.productType === productType
                &&
                tornado.resource === resource
              )
            })
            if (teaTornado.show && !hasThisProductTypeResourcePairTornadoAlreadyBeenAdded) {
              teaTornado.opts.yAxis[1].title.text = teaUnit; // show tornado unit on bottom of chart with dummy 2nd Y axis
              teaTornados.push(teaTornado);
              const pathway = { productType, resource };
              const isThisPathwayAddedYet = chartsGroupedByProduct[product].pathways.some(pathway => {
                return pathway.productType === productType && pathway.resource === resource
              });
              if (!isThisPathwayAddedYet) {
                chartsGroupedByProduct[product].pathways.push(pathway);
              }
            }
          });
          chartsGroupedByProduct[product].teaTornados = teaTornados;
        }
      }
    }
  }

  // const teaChartRef = React.useRef(null);

  const chartsGroupedByProductArray = [];
  for (const product in chartsGroupedByProduct) {
    chartsGroupedByProductArray.push({
      ...chartsGroupedByProduct[product],
      product: product
    })
  }

  // TODO remove below activeCases stuff, that's a placeholder for developing 4+ case UI
  // const [activeCases, setActiveCases] = React.useState([1,2,3,4,5,6,7,8,9,10].map(num => ({num: num, isSelected: false})));
  // console.log(activeCases);
  // console.log(comparisonCases);
  // console.log(fetchResponse);

  const isTwoColChartLayout = isComparisonMode || isAnyColumnFullscreened || false;

  // Future: if we ever decide to track input states in ModuleState instead of in each module component itself, we can generalize the below behavior into comparableResultsModule since it will know about the input state of all cases
  const attemptToRunAllCases = () => {
    const caseIndexesWithValidInputs: number[] = [];
    arrayOfComparisonCaseInputHandlers.forEach((comparisonCaseInputHandler, comparisonIndex) => {
      const areInputsInAllStagesValid = comparisonCaseInputHandler.arrayOfStageInputHandlers.every(handler => {
        const areThereInputsInThisStage = Object.keys(handler.inputStates).length > 0;
        let areThereAnyInvalidInputs = false;
        if (areThereInputsInThisStage && !handler.isValid) {
          areThereAnyInvalidInputs = true;
        }
        return !areThereAnyInvalidInputs;
      });
      const isThisCaseActive = comparisonCases?.length && comparisonIndex < comparisonCases?.length;
      const isThisCaseAlreadyRun = !!comparisonCases?.[comparisonIndex]?.data?.analysisResult;
      if (areInputsInAllStagesValid && isThisCaseActive && !isThisCaseAlreadyRun) {
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
          const inputHandler = arrayOfComparisonCaseInputHandlers[comparisonIndex];
          return {
            customData: {
              inputValuesByStage: getInputValuesByStage({
                stages,
                arrayOfStageInputHandlers: inputHandler.arrayOfStageInputHandlers,
                nodesChosen: inputHandler.nodesChosen,
              }),
              customInputValues: getCustomInputValues({inputHandler, stages}),
            }
          }
        }
      }),
      dispatch,
    })
  }

  useEventListener('attemptToRunAllCases', attemptToRunAllCases)
  useEventListener('saveBatch', handleSaveBatch);

  const numChartGroups = chartsGroupedByProductArray.length;

  return (
    <Layout
      pathname={location?.pathname ?? ""}
      padResults={false}
      secondCol={[
        <>
          <div className="divide-y">
            {chartsGroupedByProductArray.map(charts => (
              <ProductChartGroup
                charts={charts}
                isTwoColChartLayout={isTwoColChartLayout}
                numChartGroups={numChartGroups}
              />
            ))}
          </div>
        </>
      ]}
    >
      <ComparisonRow
        sidebar={
          <>
            <SavedBatchControls />
            {comparisonCases && comparisonCases.length > 3 &&
              <div style={{flexBasis: '1px'}} className="w-full py-2 !pr-5 overflow-y-scroll max-h-[250px] relative">
                <div className="text-lg font-bold">Edit inputs for:</div>
                <svg xmlns="http://www.w3.org/2000/svg" className="absolute top-2 right-2 h-8 w-8 p-1 rounded border border-gray-200 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
                <div className="text-gray-500">(Choose up to 3)</div>

                {/* <List
                  values={activeCases}
                  onChange={({ oldIndex, newIndex }) =>
                    setActiveCases(arrayMove(activeCases, oldIndex, newIndex))
                  }
                  renderList={({ children, props }) => <div {...props}>{children}</div>}
                  renderItem={({ value, props, isDragged }) => {
                    const numCasesSelected = activeCases.filter(activeCase => activeCase.isSelected).length;
                    // const isSelected = value <= 3;
                    const isTogglable = value.isSelected || numCasesSelected < 3;
                    return (
                      <div
                        {...props}
                        role="button"
                        className="py-1"
                        onMouseDown={(e) => {
                          if (!isDragged) {
                            console.log('click')
                            setActiveCases(activeCases.map((activeCase, index) => {
                                if (activeCase.num !== value.num) {
                                  return activeCase;
                                }
                                return {
                                  ...activeCase,
                                  isSelected: !activeCase.isSelected
                                }
                              })
                            )
                          }
                        }}
                        title={isTogglable ? '' : 'Deselect a case first'}
                      >
                        <div
                          // role="button"
                          className={`${value.isSelected ? `bg-gray-700 text-gray-100` : `bg-gray-100`} ${isTogglable ? 'cursor-pointer' : 'cursor-not-allowed'} relative py-1 px-2 rounded flex items-center`}
                          
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                          </svg>
                          {`New Case ${value.num}`}
                          <svg
                            className="cursor-pointer ml-auto h-7 w-7 p-1 text-gray-400 hover:text-red-500 group-focus:text-gray-500"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              // const shouldDelete = confirm('Delete "' + getCaseNameById(savedCase.id) + '"?')
                              // if (shouldDelete) {
                              //   dispatch({type: 'deleteSavedCaseIds', value: [savedCase.id]});
                              //   closeMenu();
                              // }
                            }}
                          >
                            <title>Remove from comparison</title>
                            <path
                              fillRule="evenodd"
                              d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                              clipRule="evenodd"
                            />
                          </svg>
                      </div>
                    </div>
                    )
                  }}
                /> */}

                {comparisonCases.map((comparisonCase, comparisonIndex) => {
                  const isSelected = false;
                  const numCasesSelected = activeCases.filter(activeCase => activeCase.isSelected).length;
                  const isTogglable = isSelected || numCasesSelected < 3;
                  return (
                    <div
                      key={comparisonIndex}
                      className={`${isSelected ? `bg-gray-700 text-gray-100` : `bg-gray-100`} ${numCasesSelected >= 3 && !isSelected ? 'cursor-not-allowed' : 'cursor-pointer'} relative py-1 px-2 rounded my-2 flex items-center`}
                      title={isTogglable ? '' : 'Deselect a case first'}
                      onClick={(e) => {
                        if (isTogglable) {
                          // setActiveCases(activeCases.map((activeCase, index) => {
                          //   if (activeCase.num !== num) {
                          //     return activeCase;
                          //   }
                          //   return {
                          //     ...activeCase,
                          //     isSelected: !activeCase.isSelected
                          //   }
                          // }))
                        }
                      }}
                    >
                      {/* <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                      </svg> */}
                      <div className="pl-1">{getCaseNameFromComparisonCaseAtIndex(comparisonCase, comparisonIndex)}</div>
                      <svg
                        className="cursor-pointer ml-auto h-7 w-7 p-1 text-gray-400 hover:text-red-500 group-focus:text-gray-500"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          // const shouldDelete = confirm('Delete "' + getCaseNameById(savedCase.id) + '"?')
                          // if (shouldDelete) {
                          //   dispatch({type: 'deleteSavedCaseIds', value: [savedCase.id]});
                          //   closeMenu();
                          // }
                        }}
                      >
                        <title>Remove from comparison</title>
                        <path
                          fillRule="evenodd"
                          d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  )
                })}
              </div>
            }
          </>
        }
        content={comparisonCases?.map((comparisonCase, comparisonIndex) => {
          return (
            <div key={comparisonCase.id} id={`inputs--case-${comparisonIndex}`}>
              <PathwayCreator1Page
                comparisonIndex={comparisonIndex}
                arrayOfComparisonCaseInputHandlers={arrayOfComparisonCaseInputHandlers}
                stages={stages}
                // pathwayCreatorState={}
                // selectedProduct={selectedProduct}
                // setSelectedProduct={(product) => {
                //   const shouldChangeProduct = confirm('Are you sure?');
                //   if (shouldChangeProduct) {
                //     setSelectedProduct(product);
                //   }
                // }}
              />
            </div>
          )
        })}
      />
        
        {/* <UnifiedLCATEAInputs analyzePathways={submitAnalysis} /> */}
        {/* {allStageNodes.reverse().map(node => (
          <Accordion title={node.node.name} defaultOpen={true}>
            {node.node.activities.map(a => (
              <p>{a.name}</p>
            ))}
          </Accordion>
        ))} */}
        {/* <InputBlock>
          <Styles.Label htmlFor={`lca-indicators-select`} className="col-span-2">
            Indicator
          </Styles.Label>
          <Styles.Select
            id="lca-indicators-select"
            value={indicator}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setIndicator(e.target.value)
            }
          >
            <option key="none" value="" disabled>
              Select one
            </option>
            {indicators.map(({ value, id }) => (
              <option key={id}>{value}</option>
            ))}
          </Styles.Select>
        </InputBlock>
        {hasError ? (
          <h1 className="text-red-600 mt-10">
            There was an error running this analysis. Please try again.
          </h1>
        ) : null} */}
      {/* </div> */}
    </Layout>
  );
};

const PathwayList = ({
  pathwayIds,
  pathways,
}: {
  pathwayIds: string[];
  pathways: Record<string, SinglePathway>;
}) => {
  return (
    <div className="flex flex-col mt-2">
      <div>
        <div className="pb-2 align-middle">
          <div>
            <div className="divide-y divide-gray-200">
              <div>
                {Object.keys(pathways)
                  .filter((p) => pathwayIds.includes(p))
                  .map((p, i) => {
                    const pathway = pathways[p];
                    return (
                      <div
                        key={p}
                        className={`mb-8 ${i % 2 === 0 ? "bg-gray-100" : "bg-gray-50"}`}
                      >
                        <div className="gutter-x py-4 text-lg font-medium text-gray-900">
                          {pathway?.pathwayName}
                        </div>
                        {Object.entries(pathway.userJson).map(
                          ([stageIndex, { activityOptions, ...rest }]) => {
                            const activity = activityOptions?.find(
                              (a) => a.id === rest.activity
                            );
                            return rest?.userInput &&
                              rest?.userInputMetadata?.length > 0 ? (
                              <div
                                key={stageIndex}
                                className="gutter-x py-2 text-gray-800"
                              >
                                <div className="font-medium">{activity?.name}</div>
                                {Object.entries(rest?.userInput).map(
                                  ([slug, { value }], index) => {
                                    return (
                                      <div className="m-3 flex" key={index}>
                                        <div className="mr-2 text-gray-400">•</div>
                                        <div> {
                                          rest?.userInputMetadata?.find(
                                            (input) => input.name === slug
                                          )?.label
                                        }
                                        : <span className="font-semibold text-gray-900">{value}</span>
                                        </div>
                                      </div>
                                    );
                                  }
                                )}
                              </div>
                            ) : null;
                          }
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};