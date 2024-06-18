import React, { useState } from "react";
import { RouteComponentProps } from "@reach/router";
import * as Styles from "../styles";
import useAppMetadata from "../../hooks/useAppMetadata";
import useFleetSourceData from "../../hooks/useFleetSourceData";
import Layout from "../layout";
import { Series, FigureSet, FigureSetType, chartColors } from "../figures";
import { MultiDatasetFigure, slugifyString } from "../graphs/multiDatasetFigure";
import Accordion from "../accordion";
import { capitalStr } from "../../utils";
import { TiledColumn } from "../tiledColumn"
import { ModuleStateContext } from "../comparableResultsModule";
import { SummaryGraphCheckboxMenu } from "../graphs/summaryGraphCheckboxMenu";
import { ColumnChooser } from "../columnChooser";
import { trigger } from "../../utils/events";
import { ComparisonInputHandler, ComparisonInputHandlerContext } from "../inputHandler";

type Plot = {
  label: string;
  data: number[][];
  columns: string[];
  axis: number;
};

export type CarsAnalysisResult = {
  plots: Plot[];
  figures: {
    name: string;
    data: number[][];
    columns: string[];
  }[];
  power_figures: {
    name: string;
    data: number[][];
    columns: string[];
  }[];
};

const seriesColors: Record<string, string> = {
  // powertrains
  FCEV: chartColors.blue,
  BEV: chartColors.green,
  PHEV: chartColors.yellow,
  HEV: chartColors.orange,
  ICED: chartColors.gray,
  ICEG: chartColors.black,

  // power sources
  Hydro: chartColors.blue,
  Wind: chartColors.green,
  Other: chartColors.red,
  Solar: chartColors.yellow,
  Nuclear: chartColors.orange,
  Gas: chartColors.gray,
  Coal: chartColors.black,

  // power demand
  EV: chartColors.green,
  "non-EV": chartColors.blue,

  // fuel types
  Gasoline_Bio: chartColors.black,
  Diesel: chartColors.gray,
  Electricity: chartColors.green,
  Hydrogen: chartColors.blue,

  // emissions sources
  Tailpipe: chartColors.black,
  "Fuel production": chartColors.orange,
  "Car production": chartColors.gray,

  // one car costs
  Maintenance: chartColors.green,
  Fuel: chartColors.gray,
  "Car Sale": chartColors.black,
  Car: chartColors.black,
};

export const powertrainOrder = ["FCEV", "BEV", "PHEV", "HEV", "ICED", "ICEG"];

const seriesOrder = [
  ...powertrainOrder,

  // power sources
  "Solar",
  "Wind",
  "Other",
  "Hydro",
  "Coal",
  "Gas",
  "Nuclear",

  // fuel types
  "Hydrogen",
  "Electricity",
  "Diesel",
  "Gasoline_Bio",

  // one car
  "Maintenance",
  "Fuel",
  "Car",
];


const defaultChartOutputs = [
  "sales",
  "stock",
  "fuel use by fuel",
  "operating emissions",
];

const nameMapping: Record<string, string> = {
  "Gasoline_Bio": "Gas + bio",
};

const display = (name: string) => {
  return nameMapping[name] || name;
};

const Figures = React.memo(({
  shouldDisplayPowerFigures,
}: {
  shouldDisplayPowerFigures: boolean;
}) => {
  const [numCharts, setNumCharts] = useState<number>(4);

  const { comparisonCases, isComparisonMode, chartControlAllocation } = React.useContext(ModuleStateContext);
  const analysisResults = comparisonCases?.map(comparisonCase => {
    if (!comparisonCase.data) {
      return null;
    }
    return {
      ...comparisonCase.data?.analysisResult,
      id: comparisonCase.id
    }
  });

  if (analysisResults?.every(analysisResult => !analysisResult?.figures)) {
    return null;
  }

  return (
    <div key={1}>
      <>
        {isComparisonMode && chartControlAllocation !== 'individual' &&
          <SummaryGraphs analysisResults={analysisResults} />
        }
        <Accordion title="Fleet Results" defaultOpen={true} indentContent={false} headerClassName="h-12 mb-0 mt-[-1px]" stickyHeader={true} padContentTop={false}>
          <div>
            <TiledColumn>
              {[...Array(numCharts).keys()].map((i) => {
                return (
                  <MultiDatasetFigure
                    key={i}
                    defaultPrimaryOutput={defaultChartOutputs[i]}
                    datasetsByCase={analysisResults?.map(analysisResult => {
                      return analysisResult?.plots || []
                    })}
                    order={seriesOrder}
                    colors={seriesColors}
                    display={display}
                  />
                );
              })}
            </TiledColumn>
          </div>
          <div className="flex justify-center border-t border-gray-300">
            <button
              onClick={() => { setNumCharts(numCharts + 1); }}
              type="button"
              className="w-48 justify-center mb-12 mt-6 inline-flex items-center px-8 py-3 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="-ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
              </svg>
              Add graph
            </button>
          </div>
        </Accordion>

        <DistanceFigures analysisResults={analysisResults} />

        <OneCarFigures analysisResults={analysisResults} />
        {shouldDisplayPowerFigures &&
          <PowerFigures analysisResults={analysisResults} />
        }

      </>
    </div>
  )
})

const Fleet = ({}: RouteComponentProps): JSX.Element => {

  // const renderCount = React.useRef(0);
  const { fleet: { fleet: fleetMetadata } } = useAppMetadata();

  const { comparisonCases, maxComparisonCases, isComparisonMode, chartControlAllocation } = React.useContext(ModuleStateContext)

  const shouldDisplayPowerFigures = comparisonCases?.some(comparisonCase => comparisonCase.data?.inputValues?.fgi === 'No') || false;

  const resultsNavLinks = [
    {
      name: 'Summary',
      targetId: 'accordion--summary',
      hidden: chartControlAllocation !== 'group',
    },
    {
      name: 'Fleet',
      targetId: 'accordion--fleet-results',
    },
    {
      name: 'Per Distance',
      targetId: 'accordion--per-distance-results',
    },
    {
      name: 'Lifecycle',
      targetId: 'accordion--lifecycle-results'
    },
    {
      name: 'Power',
      targetId: 'accordion--power-grid-results',
      hidden: !shouldDisplayPowerFigures,
    },
  ]

  const shouldShowNavLinks = comparisonCases.some((comparisonCase) => !!comparisonCase?.data?.analysisResult);

  return (
    <>
    {/* <div className="py-1 px-2 bg-red-500 text-white">Fleet rendered {(renderCount.current ++)} time(s)</div> */}

    <Layout
      secondCol={[
        <Figures key="figures" shouldDisplayPowerFigures={shouldDisplayPowerFigures} />
      ]}
      resultsRibbonContent={
        <>
          {shouldShowNavLinks &&
            <div className={`flex items-center ${!isComparisonMode ? 'mx-2' : ''} h-full`}>
              {resultsNavLinks.map((navLink, index) => {
                if (!navLink.hidden) {
                  return (
                    <Styles.Button
                      color="gray"
                      size="xs"
                      key={index}
                      className="mr-3 whitespace-nowrap"
                      // className="text-gray-600 font-medium mr-4 underline cursor-pointer whitespace-nowrap"
                      onClick={(e) => {
                        e.stopPropagation();
                        trigger('openColumn', {type: 'results'})
                        setTimeout(() => {
                          trigger('scrollToAccordion', {id: navLink.targetId});
                        }, 10)
                      }}
                    >
                      {navLink.name}
                    </Styles.Button>
                  )
                } else {
                  return null;
                }
              })}
            </div>
          }
        </>

      }
    >
      <ComparisonInputHandler
        moduleMetadata={fleetMetadata}
        extraContentByCase={comparisonCases?.map((comparisonCase, comparisonIndex) => (
          <DataTable comparisonIndex={comparisonIndex} />
        ))}
      />
    </Layout>
    </>
  );
};

export default React.memo(Fleet);

const DistanceFigures = React.memo(
  ({ analysisResults }: { analysisResults: CarsAnalysisResult[] }) => {
    const data = analysisResults.find(analysisResult => {return !!analysisResult})?.figures?.[0];
    if (!data) {
      return null;
    }
    const yearIdx = data.columns.indexOf("year");
    const years: number[] = data.data.map((row) => row[yearIdx]);

    const genSeries = (type: string) => {

      return (inputs: Record<string, string>, index: number) => {
        const analysisResult = analysisResults[index];
        const vintage = inputs["vintage"];

        let name = "";
        if (type === "fuel" && vintage === "New") {
          name = "fuel_dist_sales";
        } else if (type === "fuel" && vintage === "All") {
          name = "fuel_dist_stock";
        } else if (type === "emissions" && vintage === "New") {
          name = "emission_dist_sales";
        } else if (type === "emissions" && vintage === "All") {
          name = "emission_dist_stock";
        } else if (type === "fuel_spend" && vintage === "New") {
          name = "fuel_spend_dist_sales";
        } else if (type === "fuel_spend" && vintage === "All") {
          name = "fuel_spend_dist_stock";
        } else {
          return [];
        }

        if (!analysisResult?.figures) {
          return null;
        }
        const figureData = analysisResult.figures?.find(
          ({ name: figureName }) => figureName === name
        );
        if (!figureData) {
          return [];
        }

        const series: Series[] = powertrainOrder.map((powertrain) => {
          const sizes: Record<string, string> = {
            Sedan: "sedan",
            "Light truck": "LT",
            All: "all",
          };
          const size: string = sizes[inputs["size"]];
          const column = `${powertrain}/${size}`;
          const columnIdx = figureData.columns.indexOf(column);

          const indexedFigureData: number[] = figureData.data.map((row) => {
            return row[columnIdx];
          });

          return {
            name: powertrain,
            type: "line",
            yAxis: 0,
            color: seriesColors[powertrain],
            data: indexedFigureData,
          };
        });

        if (inputs["unit"] === "(Relative to 2019)" || inputs["unit"] === "(% change from 2019)") {
          const idx2019 = years.indexOf(2019);
          series.forEach((s) => {
            const val2019 = s.data[idx2019];
            s.data = s.data.map((value: number) => {
              if (value === null) {
                return value;
              } else {
                return value / val2019;
              }
            });

            if (inputs["unit"] === "(% change from 2019)") {
              s.data = s.data.map(val => (val - 1) * 100);
            }
          });
        }

        return series;
      }
    };

    const caseIds = analysisResults?.map(item => item?.id);

    const figureSet: FigureSetType = {
      caseIds: caseIds,
      inputs: [
        {
          name: "vintage",
          label: "Age:",
          options: ["New", "All"],
        },
        {
          name: "size",
          label: "Size:",
          options: ["Sedan", "Light truck", "All"],
        },
      ],
      figures: [
        {
          title: "Fuel per distance",
          categories: years,
          inputs: [
            {
              name: "unit",
              label: '',
              options: ["(kWh/mi)", "(Relative to 2019)", "(% change from 2019)"],
            },
          ],
          series: genSeries("fuel"),
          caseIds: caseIds,
        },
        {
          title: "Operating emissions per distance",
          categories: years,
          inputs: [
            {
              name: "unit",
              label: '',
              options: ["(g/mi)", "(Relative to 2019)", "(% change from 2019)"],
            },
          ],
          series: genSeries("emissions"),
          caseIds: caseIds,
        },
        {
          title: "Fuel spend per distance",
          categories: years,
          inputs: [
            {
              name: "unit",
              label: '',
              options: ["($/mi)", "(Relative to 2019)", "(% change from 2019)"],
            },
          ],
          series: genSeries("fuel_spend"),
          caseIds: caseIds,
        },
      ],
    };

    return <FigureSet figureSet={figureSet} wrapInAccordion={true} accordionTitle="Per Distance Results" />
  }
);
DistanceFigures.displayName = "DistanceFigures";

function areNextAnalysisResultsSameAsPrevious(prev, next) {
  const prevSavedCaseIds = prev?.analysisResults?.map(item => item?.id);
  const nextSavedCaseIds = next?.analysisResults?.map(item => item?.id);
  console.log(prevSavedCaseIds, nextSavedCaseIds)
  const areEqual = prevSavedCaseIds.every((id, index) => {
    return id === nextSavedCaseIds[index]
  });
  console.log(areEqual);
  return areEqual;
}

const OneCarFigures = React.memo(
  ({ analysisResults }: { analysisResults: CarsAnalysisResult[] }) => {

    // const { comparisonCases } = React.useContext(ModuleStateContext);
    // const analysisResults = comparisonCases?.map(comparisonCase => comparisonCase.data?.analysisResult);
    // const comparisonCaseIds = analysisResults?.map(item => item.id);

    // const renderCount = React.useRef(0);

    const genSeries = (prefix: String) => {

      return (inputs: Record<string, string>, index: number) => {

        const analysisResult = analysisResults[index];
        // return analysisResults.map(analysisResult => {
          if (!analysisResult || !analysisResult.figures) {
            return null;
          }
          const figures = analysisResult.figures;

          const sizes: Record<string, string> = {
            Sedan: "sedan",
            "Light truck": "LT",
          };

          const size: string = sizes[inputs["size"]];
          const year = inputs["year"];

          const name = `${prefix}_${size}_${year}`;

          const figureData = figures.find(
            ({ name: figureName }) => figureName === name
          );
          if (!figureData) {
            return [];
          }

          const icegData = figureData.data.find((row) => {
            return row[0].toString() === "ICEG";
          });

          const icegTotal =
            icegData?.slice(1).reduce((sum, val) => sum + val, 0) || 1;

          const series: Series[] = figureData.columns.slice(1).map((source) => {
            const columnIdx = figureData.columns.indexOf(source);

            const data: number[] = figureData.data.map((row) => {
              return row[columnIdx];
            });

            const unit = inputs["unit"];
            if (unit === "(Relative to total)") {
              for (let i = 0; i < data.length; i++) {
                const total = figureData.data[i]
                  .slice(1)
                  .reduce((sum, val) => sum + val, 0);
                data[i] /= total;
              }
            } else if (unit === "(Relative to ICEG total)") {
              for (let i = 0; i < data.length; i++) {
                data[i] /= icegTotal;
              }
            }

            const seriesName = capitalStr(source);

            return {
              name: seriesName,
              color: seriesColors[seriesName],
              type: "column",
              stacking: "normal",
              yAxis: 0,
              data,
            };
          });

          return series.sort((a, b) => {
            const ai = seriesOrder.indexOf(a.name);
            const bi = seriesOrder.indexOf(b.name);
            return ai - bi;
          });
        // })
      };
    };

    const caseIds = analysisResults?.map(item => item?.id);



    const figureSet = {
      caseIds: caseIds,
      inputs: [
        {
          name: "year",
          label: "Sale year:",
          options: ["2020", "2030"],
        },
        {
          name: "size",
          label: "Size:",
          options: ["Sedan", "Light truck"],
        },
      ],
      figures: [
        {
          title: "Lifecycle emissions per distance",
          categories: powertrainOrder,
          chartOptions: {
            xAxis: { labels: { step: 1 }, reversed: true },
          },
          inputs: [
            {
              name: "unit",
              label: '',
              options: [
                "(g/mi)",
                "(Relative to total)",
                "(Relative to ICEG total)",
              ],
            },
          ],
          series: genSeries("onecar"),
          caseIds: caseIds,
        },
        {
          title: "Lifecycle cost per distance",
          categories: powertrainOrder,
          chartOptions: {
            xAxis: { labels: { step: 1 }, reversed: true, },
          },
          inputs: [
            {
              name: "unit",
              label: '',
              options: [
                "($/mi)",
                "(Relative to total)",
                "(Relative to ICEG total)",
              ],
            },
          ],
          series: genSeries("costs"),
          caseIds: caseIds,
        },
      ],
    };
    return (
      <>
        {/* <div className="py-1 px-2 bg-red-500 text-white">OneCarFigures rendered {(renderCount.current ++)} time(s)</div> */}
        <FigureSet figureSet={figureSet} wrapInAccordion={true} accordionTitle="Lifecycle Results"/>
      </>
    )
    // return <FigureSet figureSet={figureSet} />;
  }//, areNextAnalysisResultsSameAsPrevious
);
OneCarFigures.displayName = "OneCarFigures";

const PowerFigures = React.memo(
  ({ analysisResults }: { analysisResults: CarsAnalysisResult[] }) => {
    const years = [2020, 2035, 2050];

    const caseIds = analysisResults?.map(item => item?.id);

    const hours: number[] = [];
    // NB: this array is zero-indexed and includes 24, resulting in
    // a length of 25. This is convenient for creating HighCharts
    // labels but `hours` should not be used for actual time conversions.
    for (let hour = 0; hour <= 24; hour++) {
      hours.push(hour);
    }

    const genSeries = (name: string, type: string) => {
      return (inputs: Record<string, string>, index: number) => {
        const analysisResult = analysisResults[index];
        if (!analysisResult) {
          return null;
        }
        const year = inputs["year"];
        const item = analysisResult.power_figures?.find((figure) => {
          return figure.name == `${name}_${year}`;
        });

        if (!item) {
          return [];
        }

        const series: Series[] = item.columns
          .map((column, idx) => {
            const data: number[] = item.data.map((row) => {
              return row[idx];
            });

            return {
              name: column,
              type,
              yAxis: 0,
              color: seriesColors[column],
              data,
            };
          })
          .sort((a, b) => {
            const ai = seriesOrder.indexOf(a.name);
            const bi = seriesOrder.indexOf(b.name);
            return ai - bi;
          });

        return series;
      };
    };

    const chartOptions = {
      // "xAxis.labels.step": 4,
      xAxis: {
        labels: {
          step: 4,
        },
      },
    };

    const figureSet = {
      caseIds: caseIds,
      inputs: [
        {
          name: "year",
          label: "Year:",
          options: years.map((year) => year.toString()),
        },
      ],
      figures: [
        {
          title: "Power demand (GW) vs. hour, average day in year",
          categories: hours.map((hour) => hour.toString()),
          inputs: [],
          series: genSeries("power_demand", "area"),
          chartOptions,
          caseIds: caseIds,
        },
        {
          title: "Power generation (GW) vs. hour, average day in year",
          categories: hours.map((hour) => hour.toString()),
          inputs: [],
          series: genSeries("power_generation", "area"),
          chartOptions,
          caseIds: caseIds,
        },
        {
          title: "Power generation (GW) vs. hour, average day in year",
          categories: hours.map((hour) => hour.toString()),
          inputs: [],
          series: genSeries("power_generation", "line"),
          chartOptions,
          caseIds: caseIds,
        },
      ],
    };

    return (
      <FigureSet figureSet={figureSet} wrapInAccordion={true} accordionTitle="Power Grid Results"/>
    )
  }
);
PowerFigures.displayName = "PowerFigures";

const SummaryGraphs = ({analysisResults}: {analysisResults: CarsAnalysisResult[]}) => {
  const chartIndexes = [
    // 'lifecycle emissions car prod & op',
    // 'lifecycle emissions since 2019',
    // 'cost',
    0, // lifecycle emissions, prod & op
    1, // lifecycle emissions since 2019
    2, // cost
  ]
  const nonEmptyAnalysisResult = analysisResults.find(analysisResult => !!analysisResult?.plots)
  const variables = nonEmptyAnalysisResult?.plots.filter(plot => plot.axis === 1).map(plot => plot.label) || []; // we're using the right axis variables from multi dataset plots
  const [variableIndexesPlotted, setVariableIndexesPlotted] = React.useState(chartIndexes);

  const sortedVariableIndexesPlotted = variableIndexesPlotted.sort(function(a, b) {
    return a - b;
  });

  const [unit, setUnit] = React.useState('raw');

  const units = [
    {
      name: 'Default Unit',
      value: 'raw',
    },
    {
      name: 'Relative to 2019',
      value: 'relative',
    }
  ]

  const [numCols, setNumCols] = React.useState(3);

  return (
    <Accordion
      title="Summary"
      defaultOpen={true}
      stickyHeader={true}
      padContentTop={false}
      headerClassName="h-12"
      headerLayout="comparisonRow"
      headerContentWhenOpen={
        <div className="flex items-center h-full col-span-3">
          <div className="flex items-center h-full">
            <SummaryGraphCheckboxMenu
              variables={variables}
              variableIndexesPlotted={variableIndexesPlotted}
              setVariableIndexesPlotted={setVariableIndexesPlotted}
            />
            <Styles.Select
              className="!w-auto"
              defaultValue={unit}
              onChange={(e) => {
                console.log(e.target.value);
                setUnit(e.target.value);
              }}
            >
              {units.map(unit => <option key={unit.value} value={unit.value}>{unit.name}</option>)}
            </Styles.Select>
          </div>
          <div className="flex items-center ml-auto">
            <ColumnChooser numCols={numCols} setNumCols={setNumCols} className="ml-auto" />
          </div>
        </div>
      }
    >
      {/* <StickyFigureControls comparisonModeTop={'9.5rem'}>

      </StickyFigureControls> */}
      <div>
        <TiledColumn numCols={numCols}>
          {sortedVariableIndexesPlotted.map((chartIndex, i) => {
            return (
              <div className="pl-2 pr-4" key={chartIndex}>
                <MultiDatasetFigure
                  defaultSecondaryOutput={slugifyString(variables[chartIndex])}
                  // defaultSecondaryIndex={chartIndex}
                  showSecondarySeriesOnly={true}
                  datasetsByCase={analysisResults?.map(analysisResult => {
                    return analysisResult?.plots || []
                  })}
                  showAllCasesOnOneChart={true}
                  order={seriesOrder}
                  colors={seriesColors}
                  display={display}
                  title={variables[chartIndex]}
                  summaryGraphUnit={unit}
                />
              </div>
            );
          })}
        </TiledColumn>
      </div>
    </Accordion>
  )
}

const DataTable = ({comparisonIndex}: {comparisonIndex: number}) => {
  const nodes = useFleetSourceData();


  const { comparisonCases } = React.useContext(ModuleStateContext);

  const isFocusModeActive = comparisonCases?.[comparisonIndex]?.isFocusModeActive

  if (isFocusModeActive) {
    return null;
  }

  const arrayOfComparisonCaseInputHandlers = React.useContext(ComparisonInputHandlerContext);

  const region = arrayOfComparisonCaseInputHandlers?.[comparisonIndex]?.inputStates['region']?.value;

  const filteredRegionData = nodes.filter((node) => node.Region === region);
  if (region) {
    return (
      <div className="mt-8 mb-3">
        <Accordion title="Data Source Defaults *" theme="subtle">
          <div className="flex flex-col">
            <div className="-my-2 w-full">
              <div className="py-2 align-middle inline-block w-full">
                <div className="w-full overflow-x-scroll">
                  <table className="divide-y divide-gray-200 mt-2">
                    <thead className="bg-gray-50">
                      <tr>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Variable
                        </th>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Source Abbrev.
                        </th>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Source
                        </th>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                        >
                          {/* <span className="sr-only">Source 1</span> */}
                          Source 1
                        </th>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                        >
                          {/* <span className="sr-only">Source 2</span> */}
                          Source 2
                        </th>
                        <th
                          scope="col"
                          className="py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                        >
                          {/* <span className="sr-only">Source 3</span> */}
                          Source 3
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredRegionData.map((node, i) => (
                        <tr
                          key={`${node.Source_Description___click_for_URL_}-${i}`}
                          className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
                        >
                          <td className="px-2 py-4 text-xs font-medium text-gray-900">
                            {node.Variable_Description}
                          </td>
                          <td className="px-2 py-4 text-xs text-gray-500">
                            {node.Source__Abbreviation}
                          </td>
                          <td className="px-2 py-4 text-xs text-gray-500">
                            {node.source_description_URL.startsWith("http") ? (
                              <a
                                className="text-blue-600 hover:text-blue-900 visited:text-purple-600"
                                href={node.source_description_URL}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {node.Source_Description___click_for_URL_}
                              </a>
                            ) : (
                              node.Source_Description___click_for_URL_
                            )}
                          </td>
                          <td className="px-2 py-4 text-xs text-gray-500">
                            {node.Source_1 ? (
                              node.source_1_URL.startsWith("http") ? (
                                <a
                                  className="text-blue-600 whitespace-nowrap hover:text-blue-900 visited:text-purple-600"
                                  href={node.source_1_URL}
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  {node.Source_1}
                                </a>
                              ) : (
                                node.Source_1
                              )
                            ) : null}
                          </td>
                          <td className="px-2 py-4 text-xs text-gray-500">
                            {node.Source_2 ? (
                              node.source_2_URL.startsWith("http") ? (
                                <a
                                  className="text-blue-600 whitespace-nowrap hover:text-blue-900 visited:text-purple-600"
                                  href={node.source_2_URL}
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  {node.Source_2}
                                </a>
                              ) : (
                                node.Source_2
                              )
                            ) : null}
                          </td>
                          <td className="px-2 py-4 text-xs text-gray-500">
                            {node.Source_3 ? (
                              node.source_3_URL.startsWith("http") ? (
                                <a
                                  className="text-blue-600 whitespace-nowrap hover:text-blue-900 visited:text-purple-600"
                                  href={node.source_3_URL}
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  {node.Source_3}
                                </a>
                              ) : (
                                node.Source_3
                              )
                            ) : null}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 text-xs">
            *Data source tables will include non-default user-selected sources in
            future update.
          </div>
        </Accordion>
      </div>
    );
  } else {
    return null;
  }

};
