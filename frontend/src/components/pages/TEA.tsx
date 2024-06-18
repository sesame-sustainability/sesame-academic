import React from "react";
import * as Sentry from "@sentry/browser";
import { navigate, Link } from "gatsby";
import { RouteComponentProps } from "@reach/router";
import { v4 as uuidv4 } from "uuid";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import useQueryString from "use-query-string";
import * as Styles from "../styles";
import UserInputs, { InputBlock } from "../userInputs";
import { groupByKeys, formatUserInput, roundToHundredth } from "../../utils";
import { bodyFontFamily, CHART_ANIMATION_DURATION, colors } from "../../utils/constants";
import useUserInputs from "../../hooks/useUserInputs";
import useAppMetadata from "../../hooks/useAppMetadata";
import useLocalStorage from "../../hooks/useLocalStorage";
import useClient from "../../hooks/useClient";
import Layout from "../layout";
import Modal from "../modal";
import { Toggle } from "../toggle";
import { ChartExportButton } from "../chartExportButton";
import { chartColors, maxBarWidth, Series, valueFormatter } from "../figures";
import { BAR_CHART_LEGEND_Y, BAR_CHART_SPACING_BOTTOM, getLCATEABarChartHeight } from "../pathwayAnalysisGraph";
import { areaChartColors } from "./pps";

const ENDPOINT = `/tea/analysis`;
const CHART_HEIGHT = "600px";
const LABEL_CLASSES = `flex col-span-2 items-center h-full`;

// interface ChartOptions {
//   chart: { style: { fontFamily: string }; type: string; height: string };
//   credits: { enabled: boolean };
//   title: { text: string };
//   xAxis: {
//     categories: (string | number)[] | undefined;
//   };
//   yAxis: {
//     min?: number;
//     title: { text?: string };
//     stackLabels: {
//       enabled: boolean;
//       style: {
//         fontWeight: string;
//         color: string;
//       };
//     };
//   };
//   plotOptions: {
//     bar: {
//       stacking: string;
//       dataLabels: {
//         enabled: boolean;
//       };
//     };
//   };
//   legend: { reversed: boolean };
//   series: { name: string; data: number[] }[];
// }

const importedColorsFromPPSWithLowercaseKeys: Record<string, string> = Object.keys(areaChartColors).reduce((acc, key) => {
  acc[key.toLowerCase()] = areaChartColors[key]
  return acc
}, {})

const teaChartColors = {
  'capex': chartColors.black,
  'capital': chartColors.black,
  'fixed': chartColors.indigo_light,
  // 'variable': chartColors.orange,
  'fuel (gas or power)': chartColors.orange,
  'fuel': chartColors.orange,
  'non-fuel variable': chartColors.yellow,
  'tax': colors.purple['800'],
  'h2 transport': chartColors.green,
  'co2 transport': chartColors.yellow,
  'co2 storage': chartColors.gray,
  'delivery': chartColors.green,
  ...importedColorsFromPPSWithLowercaseKeys,
}

export const teaChartOptions = ({
  teaData,
  categories,
  isChartStacked,
}: {
  teaData: (PathwayAnalysisResponse & { data: Data[] })[] | undefined;
  categories: string[];
  isChartStacked: boolean;
}) => {

  const config = {//}: ChartOptions = { // disabled TS interface here b/c it was becoming onerous to keep interface updated when adding new chart config props
    chart: {
      type: "bar",
      // height: '60%',
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
      height: CHART_HEIGHT,
      animation: false,
      spacingBottom: BAR_CHART_SPACING_BOTTOM,
    },
    credits: {
      enabled: false,
    },
    title: {
      // enabled: false,
      text: null,
    },
    navigation: {
      buttonOptions: {
        enabled: false
      },
    },
    xAxis: {
      labels: {
        enabled: !!categories?.length,
      },
      categories,
      reversed: (isChartStacked ? undefined : true),
      plotLines: categories?.length <= 1 ? [] : new Array(categories.length - 1).fill(null).map((o, index) => ({
        color: '#d1d5db',
        width: 1,
        value: index + 0.5 // Need to set this probably as a var.
      })),
    },
    tooltip: {
      // pointFormat: "{series.name}: {point.y}",
      headerFormat: "<b>{point.x}</b><br/>",
      pointFormatter: function(): string {
        return (
          `${this.series.name}: ${valueFormatter({value: this.y})}${isChartStacked ? `<br>Total: ${valueFormatter({value: this.total})}` : ''}`
        )
      },
      borderWidth: 0,
      borderRadius: 5,
      borderColor: 'transparent',
      backgroundColor: 'rgba(0,0,0,0.75)',
      shadow: false,
      style: {
        color: '#eee'
      }
    },
    yAxis: {
      // min: 0,
      title: {
        text: "Cost",
      },
      stackLabels: {
        enabled: true,
        style: {
          fontWeight: "bold",
          // backgroundColor: '#999',
          color: "#666",
        },
        formatter: function(): string {
          const value = this.total;
          return valueFormatter({value});
        },
      },
      reversedStacks: isChartStacked ? false : undefined,
    },
    plotOptions: {
      bar: {
        stacking: isChartStacked ? "normal" : '',
        borderWidth: 0,
        groupPadding: 0.15,
        dataLabels: {
          enabled: !isChartStacked,
          color: "#666",
          formatter: function(): string {
            const value = this.y;
            return valueFormatter({value});
          },
        },
        maxPointWidth: maxBarWidth,
        pointWidth: isChartStacked ? maxBarWidth : 15,
      },
    },
    series: [] as Series[],
    legend: {
      // reversed: true,
      itemStyle: {
        fontWeight: 'normal',
      },
      itemMarginTop: 1,
      itemMarginBottom: 3,
      floating: true,
      y: BAR_CHART_LEGEND_Y,
    },
  };

  if (!teaData || teaData.length <= 0) return config;

  const categoryParts = new Set<string>();
  const indexed: Record<string, number> = {};

  teaData?.forEach(({ data }) => {
    data?.forEach(({ cost_category, cost_category_by_parts, value }) => {
      const label = `${cost_category} - ${cost_category_by_parts}`;
      if (typeof value === "number") {
        indexed[label] = value;
      }
      if (
        typeof cost_category === "string" &&
        typeof cost_category_by_parts === "string" &&
        !categoryParts.has(label)
      ) {
        categoryParts.add(label);
      }
    });
  });

  // all series units should be the same
  config.yAxis.title.text = teaData[0].unit || "Cost";

  categoryParts.forEach((name) => {
    const seriesData: number[] = [];
    const [cat, ...rest] = name.split(" - ");
    const subcat = rest.join(" - ");

    if (cat === subcat) {
      name = cat;
    }

    teaData.forEach((res) => {
      let value = 0;

      res.data.forEach((data) => {
        if (
          data.cost_category === cat &&
          data.cost_category_by_parts === subcat
        ) {
          value = roundToHundredth(
            typeof data.value === "string" ? parseFloat(data.value) : data.value
          );
        }
      });
      seriesData.push(value);
    });
    const chartColorKey = name.toLowerCase();
    config.series.push({
      name,
      data: seriesData,
      color: teaChartColors[chartColorKey],
    });
  });

  const numBars = isChartStacked ? (categories.length || 1) : config.series.map(s => s.data?.length).reduce((acc, o) => acc + o)
  const numCases = teaData.length

  config.chart.height = String(getLCATEABarChartHeight({numBars, numBarGroups: numCases, isChartStacked}))

  return config;
};

const TeaTable = ({ data }: { data: (string | number)[][] }): JSX.Element => {
  return (
    <table>
      <thead>
        <tr>
          {
            // first row is the header
            data[0].map((item, i) => {
              return <th key={i}>{item}</th>;
            })
          }
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-100">
        {data.slice(1).map((row, i) => {
          return (
            <tr key={i} className="border-t border-gray-200">
              {row.map((item, j) => {
                return <td key={j}>{item}</td>;
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

const TEAAnalysisTab = ({
  // location,
}: {
  // location: RouteComponentProps["location"];
}): JSX.Element | null => {
  const { client } = useClient();
  const {
    allAnalysis: { nodes: analysisTypes },
  } = useAppMetadata();
  const [pathways, setTeaPathways] = useLocalStorage<
    Record<
      string,
      {
        inputs: Record<string, InputState>;
        indicator: string;
        userInputs: UserInputProperties[];
      }
    >
  >("TEA_pathways", {});
  const [indicator, setIndicator] = React.useState(
    analysisTypes[0].analysis.name
  );
  const userInputs = React.useMemo(() => {
    return analysisTypes.find(({ analysis: { name } }) => name === indicator)
      ?.analysis.user_inputs;
  }, [analysisTypes, indicator]);

  // what is the source here if there is no pathway? need a source in
  // the URL to be able to fetch the options
  const [inputs, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(
    userInputs,
    indicator,
    "/tea/analyses"
  );
  const [fetchResponse, setFetchResponse] =
    React.useState<(PathwayAnalysisResponse & { data: Data[] })[]>();
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [pathwayIds, setPathwayIds] = React.useState<string[]>([]);
  const [query, setQuery]: [
    { pathways: string },
    React.Dispatch<React.SetStateAction<{ pathways: undefined | string }>>
  ] = useQueryString(location, navigate);
  const [loadedInputs, setLoadedInputs] =
    React.useState<Record<string, InputState> | undefined>(undefined);
  const [loadedIndicator, setLoadedIndicator] =
    React.useState<string | undefined>(undefined);
  const [loadedUserInputs, setLoadedUserInputs] =
    React.useState<UserInputProperties[] | undefined>(undefined);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isChartStacked, setIsChartStacked] = React.useState(true);
  const chartRef = React.useRef(null);

  React.useEffect(() => {
    if (query.pathways && pathways[query.pathways]) {
      setLoadedInputs(pathways[query.pathways].inputs);
      setLoadedIndicator(pathways[query.pathways].indicator);
      setLoadedUserInputs(pathways[query.pathways].userInputs);
    }
  }, []);

  React.useEffect(() => {
    if (query.pathways && typeof query.pathways === "string") {
      setPathwayIds(query.pathways?.split(","));
    } else {
      setPathwayIds([]);
    }
  }, [query.pathways]);

  const chartOptions = React.useMemo(() => {
    return teaChartOptions({
      teaData: fetchResponse,
      categories: pathwayIds.map((id) => pathways[id].indicator),
      isChartStacked: isChartStacked,
    });
  }, [fetchResponse, pathways, pathwayIds, isChartStacked]);

  const handleSave = () => {
    if (fetchResponse) {
      setIsModalOpen(true);
      setTeaPathways({
        ...pathways,
        [uuidv4()]: { indicator, inputs, userInputs },
      });
    }
  }

  const submit = async () => {
    if (!isValid && !loadedUserInputs && !query.pathways) return;

    const formattedPathways = [];

    if (!query.pathways) {
      // filter out invisible inputs, which are not valid
      // for the current indicator
      const user_inputs = [];
      for (const { name } of loadedUserInputs || userInputs || []) {
        const i = loadedInputs || inputs;
        if (i[name].isVisible) {
          user_inputs.push(formatUserInput(i[name].value));
        }
      }
      formattedPathways.push({
        analysis_name: loadedIndicator || indicator,
        user_inputs,
      });
    } else {
      pathwayIds.forEach((id) => {
        const user_inputs = [];
        const p = pathways[id];
        // filter out invisible inputs, which are not valid
        // for the current indicator
        for (const name of Object.keys(p.inputs)) {
          if (p.inputs[name].isVisible) {
            user_inputs.push(formatUserInput(p.inputs[name].value));
          }
        }
        formattedPathways.push({
          analysis_name: p.indicator,
          user_inputs,
        });
      });
    }

    try {
      setIsLoading(true);
      const responses = await Promise.all(
        formattedPathways.map(
          async (body) =>
            await client(ENDPOINT, {
              body,
            })
        )
      );
      setFetchResponse(
        responses.map((res) => {
          return groupByKeys(
            res as PathwayAnalysisResponseWithUnformattedData,
            ["cost_category", "cost_category_by_parts"]
          );
        })
      );
      setIsLoading(false);
    } catch (err) {
      Sentry.captureEvent({
        message: `Error: ${ENDPOINT}`,
        extra: {
          err: JSON.stringify(err),
          body: JSON.stringify(formattedPathways),
        },
      });
      setFetchResponse(err.message);
      setIsLoading(false);
    }
  };

  const figureTitle = 'TEA Analysis';

  if (!userInputs) return null;

  return (
    <Layout
      // pathname={location?.pathname ?? ""}
      handleRun={submit}
      isRunButtonDisabled={(!isValid && !loadedInputs) || isLoading}
      // handleSave={handleSave}
      isSaveButtonDisabled={isLoading || !fetchResponse}
      padResults={true}
      secondCol={[
        fetchResponse ? (
          <div className="relative">
            <Styles.ChartTitle>{figureTitle}</Styles.ChartTitle>
            <ChartExportButton chartTitle={figureTitle} chartRef={chartRef} />
            <HighchartsReact
              ref={chartRef}
              key={status}
              highcharts={Highcharts}
              options={JSON.parse(JSON.stringify(chartOptions))}
            />
            <div className="absolute top-0 left-0">
              <Toggle label="Stack Bars" value={isChartStacked} setValue={setIsChartStacked} />
            </div>
            {fetchResponse[0].table ? (
              <TeaTable data={fetchResponse[0].table} />
            ) : null}
          </div>
        ) : <></>
        // (
        //   <HighchartsReact
        //     key={1}
        //     highcharts={Highcharts}
        //     options={{
        //       chart: {
        //         style: {
        //           fontFamily: bodyFontFamily.join(", "),
        //         },
        //         height: CHART_HEIGHT,
        //       },
        //       credits: {
        //         enabled: false,
        //       },
        //       title: {
        //         enabled: true,
        //         text: "TEA Analysis",
        //       },
        //       series: [
        //         {
        //           type: "line",
        //           name: "",
        //           data: [],
        //         },
        //       ],
        //       xAxis: {
        //         title: {
        //           enabled: true,
        //           text: "Solar",
        //         },
        //       },
        //       yAxis: {
        //         title: {
        //           enabled: true,
        //           text: "Cost",
        //         },
        //       },
        //       noData: {
        //         style: {
        //           fontWeight: "bold",
        //           fontSize: "15px",
        //           color: "#303030",
        //         },
        //       },
        //     }}
        //   />
        // ),
      ]}
    >
      <div className="gutter-x">
        <div className="">
          {/* <Styles.H2>{query.pathways ? "Analysis" : "Inputs"}</Styles.H2> */}
          <>
            {query.pathways ? (
              <>
                {Object.keys(pathways).map((key, i) => {
                  return pathwayIds.map((id) => {
                    if (id === key) {
                      const pathwayInputs = [];

                      for (const { label, name } of pathways[id].userInputs) {
                        if (
                          pathways[id].inputs[name].isVisible &&
                          pathways[id].inputs[name].value
                        ) {
                          pathwayInputs.push({
                            label,
                            value: pathways[id].inputs[name].value,
                          });
                        }
                      }
                      return (
                        <React.Fragment key={`${key}-${i}`}>
                          <details className="mb-2">
                            <summary className="mb-2">
                              {pathways[key].indicator} Pathway {i}
                            </summary>
                            {pathwayInputs.map((input, idx) => {
                              if (!input.label || !input.value) return null;
                              return (
                                <div
                                  key={`${input.label}-${input.value}`}
                                  className={`text-xs py-1 ${
                                    idx % 2 === 0 ? "bg-white" : "bg-gray-50"
                                  }`}
                                >
                                  <span className={``}>{input.label}</span>
                                  <span className="text-xs font-semibold float-right">
                                    {input.value}
                                  </span>
                                </div>
                              );
                            })}
                          </details>
                        </React.Fragment>
                      );
                    }
                  });
                })}
                <Styles.Button
                  disabled={isLoading}
                  className="mt-10 mb-10 mr-4 justify-center"
                  onClick={submit}
                >
                  {isLoading ? "Running..." : "Run"}
                </Styles.Button>
                <Styles.Button
                  disabled={isLoading}
                  className="mt-10 mb-10 mr-4 justify-center"
                  onClick={() => {
                    navigate(`/app/costs`);
                  }}
                >
                  Create New Pathway
                </Styles.Button>
              </>
            ) : (
              <>
                <InputBlock>
                  <Styles.Label
                    className={LABEL_CLASSES}
                    htmlFor={`tea-indicators-select`}
                    className="col-span-2"
                  >
                    Type
                  </Styles.Label>
                  <Styles.Select
                    id="tea-indicators-select"
                    value={loadedIndicator || indicator}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                      setIndicator(e.target.value);
                      setFetchResponse(undefined);
                      setLoadedInputs(undefined);
                      setLoadedIndicator(undefined);
                      setLoadedUserInputs(undefined);
                      if (query.pathways) {
                        // navigate("/app/costs");
                        setQuery({ pathways: undefined });
                      }
                    }}
                  >
                    <option key="none" value="" disabled>
                      Select one
                    </option>
                    {analysisTypes.map(({ analysis: { name } }) => (
                      <option key={name}>{name}</option>
                    ))}
                  </Styles.Select>
                </InputBlock>
                <UserInputs
                  labelClassName={LABEL_CLASSES}
                  wrapperClassName="sm:grid sm:grid-cols-3 sm:gap-4 sm:items-center"
                  errorClassName="col-span-2 mt-0 mb-2"
                  userInputs={loadedUserInputs || userInputs}
                  comparisonIndex={0}
                  inputStates={loadedInputs || inputs}
                  setInput={setInput}
                  setInputError={setInputError}
                />
                {/* <Styles.Button
                  disabled={(!isValid && !loadedInputs) || isLoading}
                  className="mt-10 mb-10 mr-4 justify-center"
                  onClick={submit}
                >
                  {isLoading ? "Running..." : "Run"}
                </Styles.Button>
                <Styles.Button
                  disabled={isLoading || !fetchResponse}
                  className="mt-10 mb-10 justify-center"
                  onClick={handleSave}
                >
                  {isLoading ? "Saving..." : "Save"}
                </Styles.Button> */}
                {typeof fetchResponse === "string" ? (
                  <h1 className="text-red-600 mt-10">
                    There was an error running this analysis. Please try again.
                  </h1>
                ) : null}
              </>
            )}
          </>
        </div>
      </div>
      <Modal showModal={isModalOpen} title="TEA Pathway Successfully Saved">
        <Styles.Button
          className="inline-flex my-4 justify-center w-full rounded-md border border-transparent px-4 py-2 text-base leading-6 font-medium text-white shadow-sm focus:outline-none transition ease-in-out duration-150 sm:text-sm sm:leading-5"
          onClick={() => setIsModalOpen(false)}
        >
          OK
        </Styles.Button>
        <span className="flex w-full rounded-md shadow-sm">
          <Link
            to="/app/costs"
            type="button"
            className="inline-flex justify-center w-full rounded-md border border-transparent px-4 py-2 bg-green-600 text-base leading-6 font-medium text-white shadow-sm hover:bg-green-500 focus:outline-none focus:border-green-700 focus:shadow-outline-green transition ease-in-out duration-150 sm:text-sm sm:leading-5"
          >
            Create new pathway
          </Link>
        </span>
      </Modal>
    </Layout>
  );
};

export default TEAAnalysisTab;
