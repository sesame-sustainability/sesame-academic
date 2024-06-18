import React, { useState, useMemo, useEffect } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { RouteComponentProps } from "@reach/router";

import useClient from "../../hooks/useClient";
import * as Styles from "../styles";
import Layout from "../layout";
import SEO from "../seo";
import UserInputs from "../userInputs";
import useUserInputs from "../../hooks/useUserInputs";
import useAppMetadata from "../../hooks/useAppMetadata";
import { capitalSentence, capitalStr } from "../../utils";
import { bodyFontFamily } from "../../utils/constants";
import { ComparisonRow } from "../comparableResultsModule";

type PowerSystemAnalysisResponse = {
  data: {
    co2: number;
    generation: number;
    heat: number;
    hour: number;
    nox: number;
    so2: number;
    state: string;
    status: string;
    total_capacity: number;
    type: string;
    year: number;
  }[];
};

const formatAnalysisName = (name: string) => {
  if (!name.includes("_")) return name;
  return name
    .split("_")
    .map((partial, i) => (i === 0 ? capitalStr(partial) : partial))
    .join(" ");
};

const PowerSystem = (): JSX.Element => {
  const { client } = useClient();
  const {
    allSystem: { nodes: powerSystemAnalyses },
  } = useAppMetadata();
  const [analysisType, setAnalysisType] = useState<string>("");

  const analysis = useMemo(() => {
    return powerSystemAnalyses.find(
      ({ system: { name } }) => name === analysisType
    )?.system;
  }, [analysisType, powerSystemAnalyses]);

  const [inputs, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(
    analysis?.user_inputs,
    analysisType,
    "/power_historic/analyses"
  );
  const [analysisResult, setAnalysisResult] =
    useState<null | PowerSystemAnalysisResponse>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSourceOrAnalysis(analysisType);
  }, [analysisType, setSourceOrAnalysis]);

  const submit = async () => {
    if (!isValid) return;
    const body = {
      analysis_name: analysisType,
      user_inputs: analysis?.user_inputs.map(({ name }) => {
        return inputs[name].value;
      }),
    };

    try {
      setLoading(true);
      const res = await client("/power_historic/analysis", { body });
      setAnalysisResult(res as PowerSystemAnalysisResponse);
      setLoading(false);
    } catch (err) {
      setAnalysisResult(err.message);
      setLoading(false);
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const chartOptions = (status: string, data: any[]) => {
    if (!analysis) return;

    const years = new Set<number>();
    data.forEach((item) => {
      years.add(item.year);
    });

    const types = new Set<string>();
    data.forEach((item) => {
      types.add(item.type);
    });

    const series: {
      name: string;
      yAxis: number;
      data: PowerSystemAnalysisResponse["data"];
      stack?: string;
      type?: string;
    }[] = [];

    if (analysis.axes.x === "year") {
      analysis.axes.y.forEach((axis) => {
        types.forEach((type) => {
          series.push({
            name: `${capitalSentence(type)} ${axis.label} (${axis.unit})`,
            yAxis: analysis.axes.y.indexOf(axis),
            stack: type,
            data: data
              .filter((item) => {
                return item.type === type;
              })
              .map((item) => {
                return item[axis.name];
              }),
          });
        });
      });
    } else {
      years.forEach((year) => {
        analysis.axes.y.forEach((axis) => {
          types.forEach((type) => {
            series.push({
              name: `${year} ${capitalSentence(type)} ${axis.label} (${
                axis.unit
              })`,
              yAxis: analysis.axes.y.indexOf(axis),
              stack: axis.name,
              type: axis.type,
              data: data
                .filter((item) => {
                  return item.year === year && item.type === type;
                })
                .map((item) => {
                  return item[axis.name];
                }),
            });
          });
        });
      });
    }

    const xData = new Set<number>();
    data.forEach((item) => {
      xData.add(item[analysis.axes.x]);
    });

    const yAxis = analysis.axes.y.map((axis) => ({
      opposite: false,
      title: {
        enabled: true,
        text: `${axis.label} (${axis.unit})`,
      },
    }));

    if (yAxis.length > 1) {
      yAxis[1].opposite = true;
    }

    return {
      chart: {
        type: "column",
        style: {
          fontFamily: bodyFontFamily.join(", "),
        },
      },
      credits: {
        enabled: false,
      },
      xAxis: {
        categories: Array.from(xData.values()).sort((a, b) => a - b),
        title: {
          enabled: true,
          text: capitalSentence(analysis.axes.x),
        },
        labels: {
          enabled: true,
        },
      },
      yAxis,
      title: {
        text: `${capitalSentence(status)}`,
      },
      plotOptions: {
        column: {
          stacking: "normal",
        },
      },
      series,
    };
  };

  const data = analysisResult ? analysisResult.data : [];
  const statuses = new Set<string>();
  data?.forEach((item) => {
    statuses.add(item.status);
  });

  const charts = Array.from(statuses.values()).map((status) => {
    const analysisResultData = analysisResult?.data.filter((item) => {
      return item.status === status;
    });
    if (!analysisResultData) return null;
    return (
      <React.Fragment key={status}>
        <br />
        <HighchartsReact
          key={status}
          highcharts={Highcharts}
          options={chartOptions(status, analysisResultData)}
        />
      </React.Fragment>
    );
  });

  // const submitButton = (
  //   <Styles.LoaderButton
  //     disabled={loading || !isValid}
  //     className="w-24 min-w-full justify-center"
  //     onClick={submit}
  //     loading={loading}
  //   />
  // )

  return (
    <Layout
      handleRun={submit}
      isRunButtonDisabled={loading || !isValid}
      // areResultsLoading={loading}
      secondCol={[
        analysisResult ? (
          <React.Fragment key={1}>{charts}</React.Fragment>
        ) : <></>
        // (
        //   <HighchartsReact
        //     key={0}
        //     highcharts={Highcharts}
        //     options={{
        //       chart: {
        //         style: {
        //           fontFamily: bodyFontFamily.join(", "),
        //         },
        //       },
        //       credits: {
        //         enabled: false,
        //       },
        //       title: {
        //         enabled: true,
        //         text: "Nearly Full Load",
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
        //           text: "Hour",
        //         },
        //       },
        //       yAxis: {
        //         title: {
        //           enabled: true,
        //           text: "Generation (MW)",
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
      <ComparisonRow
        content={
          <>
            <div className="relative mb-2 grid grid-cols-3 gap-4">
              <Styles.Label htmlFor={`power-system-analysis-type`} className="col-span-2">
                Analysis type
              </Styles.Label>
              <Styles.Select
                id={`power-system-analysis-type`}
                value={analysisType}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                  setAnalysisType(e.target.value);
                  setAnalysisResult(null);
                }}
              >
                <option key="none" value="" disabled>
                  Select one
                </option>
                {powerSystemAnalyses.map(({ system: { name } }) => (
                  <option key={name} value={name}>
                    {formatAnalysisName(name)}
                  </option>
                ))}
              </Styles.Select>
            </div>
            <UserInputs
              userInputs={flattenedUserInputs}
              inputStates={inputs}
              setInput={setInput}
              setInputError={setInputError}
            />
          </>
        }
      />
    </Layout>
  );
};

export default PowerSystem;
