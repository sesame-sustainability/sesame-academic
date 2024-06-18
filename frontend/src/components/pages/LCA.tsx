import React, { useEffect } from "react";
import * as Sentry from "@sentry/browser";
import { navigate, Link } from "gatsby";
import { RouteComponentProps } from "@reach/router";
import useQueryString from "use-query-string";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

import useLocalStorage from "../../hooks/useLocalStorage";
import useAppMetadata from "../../hooks/useAppMetadata";
import useClient from "../../hooks/useClient";
import * as Styles from "../styles";
import { groupByPathway, groupByKeys } from "../../utils";
import { tornadoChartOpts } from "../graphs/TornadoChartOpts";
import PathwayAnalysisGraph from "../pathwayAnalysisGraph";
import Layout from "../layout";
import { teaChartOptions } from "./TEA";
import { InputBlock } from "../userInputs";
import { ChartExportButton } from "../chartExportButton";
import { Toggle } from "../toggle";
import { TiledColumn } from "../tiledColumn";
import { ModuleStateContext } from "../comparableResultsModule";
import { Tooltip } from "../tooltip";

const ENDPOINT = `/lca/analysis`;

const formatSteps = (
  pathwayIds: string[],
  pathways: Record<string, SinglePathway>
) => {
  return pathwayIds.map((id) => {
    const { userJson, pathwayName } = pathways[id];
    let stepsKeys = Object.keys(userJson);

    if (userJson[0]?.activity?.includes("upstream")) {
      stepsKeys = stepsKeys.reverse();
    }

    const steps = stepsKeys.reduce<
      {
        source_id: string;
        user_inputs: (string | number)[];
      }[]
    >((acc, cur) => {
      if (userJson[cur].source) {
        const user_inputs = [];

        for (const [, { isVisible, value }] of Object.entries(
          userJson[cur].userInput
        )) {
          const formattedValue = !Number.isNaN(parseFloat(value))
            ? parseFloat(value)
            : value;

          if (isVisible) {
            user_inputs.push(formattedValue);
          }
        }

        return [...acc, { source_id: userJson[cur].source, user_inputs }];
      }
      return acc;
    }, []);

    return {
      name: pathwayName,
      steps,
    };
  });
};

let fetchResponseInMemory:
  | (PathwayAnalysisResponse & { data: Data[] })
  | undefined;

const Chart = ({ chart }) => {
  return (
    <>
      {chart.show && (
        <div key={2} className="mt-6 relative" style={{breakInside: "avoid"}}>
          <Styles.ChartTitle>
            {chart.opts?.title}
            {chart.opts?.titleTooltipContent &&
              <Tooltip data={{content: chart.opts?.titleTooltipContent}}/>
            }
          </Styles.ChartTitle>
          <ChartExportButton chartTitle={chart.opts.title} chartRef={chart.ref} />
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

const LCA = ({
  location,
}: {
  location: RouteComponentProps["location"];
}): JSX.Element => {
  const { client } = useClient();
  const {
    allIndicator: { nodes: indicators },
  } = useAppMetadata();
  const { isAnyColumnFullscreened } = React.useContext(ModuleStateContext);
  const [fetchResponse, setFetchResponse] = React.useState<
    (PathwayAnalysisResponse & { data: Data[] }) | undefined
  >(fetchResponseInMemory);
  const [teaResponse, setTeaResponse] =
    React.useState<TEAResponse>();
  const [teaName, setTeaName] = React.useState<string>("");
  const [indicator, setIndicator] = React.useState("GWP");
  const [isLoading, setIsLoading] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);
  const [pathwayIds, setPathwayIds] = React.useState<string[]>([]);
  const [pathways] = useLocalStorage<Record<string, SinglePathway>>(
    "pathways",
    {}
  );
  const formattedPathways = React.useMemo(
    () => formatSteps(pathwayIds, pathways),
    [pathwayIds, pathways]
  );

  const [query, setQuery] = useQueryString(location, navigate);

  React.useEffect(() => {
    fetchResponseInMemory = fetchResponse;
    // if there is a fetch response in memory,
    // look up the pathway Ids using pathway name and set
    // query params from the fetch response
    const idList = [];

    if (fetchResponseInMemory && pathways) {
      for (const { pathway } of Object.values(fetchResponseInMemory.data)) {
        for (const [key, value] of Object.entries(pathways)) {
          if (value.pathwayName === pathway) {
            idList.push(key);
          }
        }
      }

      if (!query.pathways && idList.length > 0) {
        setQuery({ pathways: idList.join(",") });
      }

      // if the ids in fetchResponseMemory are not the same
      // as those in the query string, unset the response in memory
      if (
        query.pathways &&
        typeof fetchResponseInMemory !== "undefined" &&
        idList.sort().join(",") !== query.pathways?.split(",").sort().join(",")
      ) {
        fetchResponseInMemory = undefined;
        setFetchResponse(undefined);
      }
    }
  }, [fetchResponse, pathways, setQuery, query.pathways]);

  React.useEffect(() => {
    if (query.pathways && typeof query.pathways === "string") {
      setPathwayIds(query.pathways?.split(","));
    }
  }, [query.pathways]);

  const submitAnalysis = async () => {
    if (!pathwayIds) return;

    setIsLoading(true);
    setHasError(false);

    const promises = [
      client(ENDPOINT, {
        body: {
          indicator,
          pathways: formattedPathways,
        },
      }),
    ];

    let performTEA = false;

    if (pathwayIds.length === 1) {
      const pathwayId = pathwayIds[0];
      const pathway = pathways[pathwayId];
      const stages = Object.values(pathway?.userJson || []);
      const teaStage = stages.find((stage) => {
        return !!stage.userInput?.["tea"];
      });

      // TODO: we should ultimately check if a TEA analysis exists with this
      // pathway's `pathway_id`
      if (teaStage) {
        // perform TEA for pathway if `tea` user input is `Yes`
        performTEA = teaStage.userInput["tea"].value === "Yes";
      }

      const wind = stages.find((stage) => {
        return stage.source === "process-windpowerproduction-default";
      });

      if (wind) {
        // always perform wind TEA (for now)
        performTEA = true;
      }
    }

    if (performTEA) {
      const pathway = formattedPathways[0];

      promises.push(
        client("/tea/analysis", {
          body: {
            pathway,
          },
        })
      );
    }

    // submit and fetch data
    const responses = await Promise.all(promises).catch((err) => {
      setIsLoading(false);
      setHasError(true);
      Sentry.captureEvent({
        message: `Error: ${ENDPOINT}`,
        extra: {
          err: JSON.stringify(err),
          pathway: JSON.stringify(formattedPathways),
        },
      });
    });
    setIsLoading(false);

    let lca = null;
    let tea = null;

    if (responses) {
      lca = responses[0];
      if (responses.length > 1) {
        tea = responses[1];
      }
    }

    if (tea) {
      setTeaResponse(
        groupByKeys(tea as PathwayAnalysisResponseWithUnformattedData, [
          "cost_category",
          "cost_category_by_parts",
        ])
      );
    }

    if (lca) {
      setFetchResponse(
        groupByPathway(lca as PathwayAnalysisResponseWithUnformattedData)
      );
    } else {
      console.warn(lca);
      setHasError(true);
      Sentry.captureEvent({
        message: `Empty response: ${ENDPOINT}`,
        extra: {
          pathway: JSON.stringify(formattedPathways),
        },
      });
    }
  };

  useEffect(() => {
    const data: Data | undefined = teaResponse?.data[0];
    if (data) {
      setTeaName(data["pathway"].toString());
    }
  }, [teaResponse]);

  const lcaUnit = fetchResponse?.unit;

  const solarTornadoChartOpts = tornadoChartOpts(fetchResponse);
  solarTornadoChartOpts.yAxis[1].title.text = lcaUnit;

  let charts = [
    {
      show: !!fetchResponse?.sensitivity,
      opts: {
        ...solarTornadoChartOpts,
        title: `${fetchResponse?.title}: Sensitivity`,
        titleTooltipContent: "Each bar corresponds to an input on left. The bar shows how much emissions change from their default value if the input is changed from its default value. See individual bars for change details.",
      },
    },
  ];

  charts = charts.map(chart => {
    return {
      ...chart,
      ref: React.useRef(null),
    }
  });

  const teaUnit = teaResponse?.unit;

  const costsTornado = {
    show: !!teaResponse?.sensitivity,
    opts: {
      ...tornadoChartOpts(teaResponse),
      title: "Costs: Sensitivity",
      titleTooltipContent: "Each bar corresponds to an input on left. The bar shows how much costs change from their default value if the input is changed from its default value. See individual bars for change details.",
    },
    ref: React.useRef(null),
  };
  costsTornado.opts.yAxis[1].title.text = teaUnit; // show tornado unit on bottom of chart with dummy 2nd Y axis

  const [isTeaChartStacked, setIsTeaChartStacked] = React.useState(true);
  const teaChartTitle = 'Costs';
  const teaChartRef = React.useRef(null);

  return (
    <Layout
      pathname={location?.pathname ?? ""}
      handleRun={submitAnalysis}
      isLoading={isLoading}
      isRunButtonDisabled={isLoading || pathwayIds.length === 0}
      padResults={true}
      // numResultsColsWhenFullscreened={2}
      secondCol={[
        <TiledColumn numCols={isAnyColumnFullscreened ? 2 : 1}>
          <div className={isAnyColumnFullscreened ? 'mr-6' : ''}>
            <PathwayAnalysisGraph
              // using random key to force the graph to
              // re-render if there was an in-memory response
              // that has been unset when the pathway ids change
              key={JSON.stringify(pathwayIds)}
              response={fetchResponse}
            />
            {charts.map(chart => {
              return fetchResponse && <Chart chart={chart} />;
            })}
          </div>
          {teaResponse && (
            <>
              <div className={`relative order-2 ${isAnyColumnFullscreened ? 'ml-6' : ''}`}>
                <Styles.ChartTitle>{teaChartTitle}</Styles.ChartTitle>
                <HighchartsReact
                  ref={teaChartRef}
                  highcharts={Highcharts}
                  options={teaChartOptions({
                    teaData: [teaResponse],
                    categories: [teaName],
                    isChartStacked: isTeaChartStacked,
                  })}
                />
                <div className="absolute top-7 left-0">  
                  <Toggle label="Stack Bars" value={isTeaChartStacked} setValue={setIsTeaChartStacked} />
                </div>
                <ChartExportButton chartRef={teaChartRef} chartTitle={teaChartTitle} />
              </div>
              <Chart chart={costsTornado} />
            </>
          )}
        </TiledColumn>
      ]}
    >
      <div className="non-comparison-cell">
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
        {pathwayIds.length === 0 ? (
          <div className="mt-8">
            Please select one or more pathways for analysis from the{" "}
            <Link
              className="text-blue-600 hover:text-blue-800"
              to="/app/saved-pathways/emissions"
            >
              pathway list
            </Link>
            .
          </div>
        ) : (
          <PathwayList pathways={pathways} pathwayIds={pathwayIds} />
        )}
      </div>
    </Layout>
  );
};

export default LCA;

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
                                className="gutter-X py-2 text-gray-800"
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
