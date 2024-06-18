import React, { useCallback, useState, useMemo, useEffect } from "react";
import { RouteComponentProps } from "@reach/router";
import merge from "deepmerge";
import { db } from '../../hooks/useDB';
import useClient from "../../hooks/useClient";
import Layout from "../layout";
import SEO from "../seo";
import PowerUserInputs, { PowerUserInputsHandler } from "../powerUserInputs";
import useUserInputs from "../../hooks/useUserInputs";
import useAppMetadata from "../../hooks/useAppMetadata";
import { Dataset, FigureSet, Series, FigureType, FigureSetType } from "../figures";
import { MultiDatasetFigure } from "../graphs/multiDatasetFigure";
import { Cell, useTable, Table, TableInputs } from "../tables";
import { generateUniqueIntId } from "../../utils";
import { ComparisonRow, ModuleDispatchContext, ModuleStateContext } from "../comparableResultsModule"
import { useLiveQuery } from "dexie-react-hooks";
import Accordion from "../accordion";

const colors = {
  blue: "#5B9BD5",
  green: "#62993E",
  yellow: "#FFC000",
  orange: "#ED7D31",
  gray: "#929292",
  black: "#000000",
  red: "#FF0000",
  purple: "purple",
};

const demandColors = {
  "non-EV": colors.blue,
  EV: colors.orange,
};

const powerSourceColors = {
  Nuclear: colors.orange,
  "Natural gas": colors.gray,
  Coal: colors.black,
  Hydro: colors.blue,
  Other: colors.purple,
  Wind: colors.green,
  Solar: colors.yellow,
};

const powerSourceOrder = [
  "Solar",
  "Wind",
  "Other",
  "Hydro",
  "Coal",
  "Natural gas",
  "Nuclear",
];

const nameMapping: Record<string, string> = {
  "Natural gas": "Gas",
  Nuclear: "Nuc",

  e_EV: "EV",
  e_nEV: "non-EV",

  e_smokestack: "Smokestack",
  e_fuel_prod: "Fuel prod",
  e_powerplant_prod: "Powerplant prod",
  e_tot: "Total",
};

const seriesOrder = [
  ...powerSourceOrder,

  "e_EV",
  "e_nEV",

  "e_powerplant_prod",
  "e_fuel_prod",
  "e_smokestack",
];

const seriesColors = {
  ...powerSourceColors,
  ...demandColors,

  e_EV: colors.orange,
  e_nEV: colors.blue,

  e_powerplant_prod: colors.black,
  e_fuel_prod: colors.orange,
  e_smokestack: colors.gray,
};

const years: number[] = [];
for (let year = 2020; year <= 2050; year++) {
  years.push(year);
}

const hours: number[] = [];
for (let hour = 0; hour < 24; hour++) {
  hours.push(hour);
}

const display = (name: string) => {
  return nameMapping[name] || name;
};

const chartOptions = ({
  xAxisStep,
  xAxisMax,
}: {
  xAxisStep: number;
  xAxisMax?: number;
}) => {
  return {
    chart: {
      height: "70%",
    },
    legend: {
      align: "center",
      layout: "horizontal",
      verticalAlign: "bottom",
    },
    xAxis: {
      labels: {
        step: xAxisStep,
      },
      max: xAxisMax,
    },
  };
};

const Figures = () => {
  // return null;
  const { comparisonCases } = React.useContext(ModuleStateContext);
  const comparisonCaseIds = comparisonCases?.map(comparisonCase => comparisonCase.id);
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
  const functionStartTime = Date.now();
  const getData = useCallback((year: number, dataset: Dataset): number[] => {
    const data: number[] =
      dataset.data.find((row) => row[0] === year)?.slice(1) || [];
    data.push(data[0]); // add hour 24 as hour 0 data
    return data;
  }, []);

  const makeComparisonFigure = useCallback(
    (figureType: string): FigureType | null => {

      // find a prototype figure here, i.e. any non-empty figure, for basing labels and axes and such off of
      const prototypeFigure = analysisResults?.find(analysisResult => !!analysisResult).figures[figureType];
      if (!prototypeFigure) {
        return null;
      }

      return {
        inputs: [],
        title: prototypeFigure.title,
        chartOptions: chartOptions({ xAxisStep: 4, xAxisMax: 24 }),
        categories: hours.map((hour) => hour.toString()),
        caseIds: comparisonCaseIds,
        // series function returns the series data for ONE chart in a comparison row, to facilitate passing in different chart input parameters per-chart if we're in individual chartControlAllocation mode
        series: (inputStates: Record<string, string>, index: number): Series[] | null => {
          if (!analysisResults?.[index]) {
            return null;
          }
          const figure = analysisResults[index].figures[figureType];
          if (!figure) {
            return null;
          }
          const year = parseInt(inputStates["year"], 10);
          return figure.datasets.map((dataset) => {
            const series = {
              name: display(dataset.label),
              yAxis: 0,
              type: dataset.type || figure.type,
              data: getData(year, dataset),
              color: dataset.color,
              dashStyle: "solid",
            };

            if (dataset.type === "line" && dataset.style === "dashed") {
              series.dashStyle = "Dash";
            }

            return series;
          });
        },
      };
    },
    [years, hours, seriesOrder, getData, comparisonCaseIds]
  );

  const figureSet: FigureSetType = { // TODO this was memoized before refactoring to allow comparisons - do we need to redo that?
    inputs: [
      {
        name: "year",
        label: "Year:",
        options: years.map((year) => year.toString()),
      },
    ],
    figures: [
      makeComparisonFigure("demand"),//analysisResults.map(analysisResult => analysisResult?.figures.demand)),
      makeComparisonFigure("generation_stacked"),//analysisResults.map(analysisResult => analysisResult?.figures.generation_stacked)),
      makeComparisonFigure("generation_line"),//analysisResults.map(analysisResult => analysisResult?.figures.generation_line)),
    ] as FigureType[],
  };
  // }//)//, [years, analysisResult, makeFigure, powerSourceColors]));

  // console.log('Figures took ' + (Date.now() - functionStartTime) + 'ms')

  return (
    <>
      <Accordion
        title="Annual Results"
        defaultOpen={true}
        indentContent={false}
        stickyHeader={true}
      >
        <MultiDatasetFigure
          datasetsByCase={analysisResults.map(analysisResult => {
            return analysisResult?.figures.multi || []
          })}
          chartOptions={chartOptions({ xAxisStep: 10 })}
          defaultPrimaryOutput="generation by power type"
          colors={seriesColors}
          order={seriesOrder}
          display={display}
        />
        <MultiDatasetFigure
          datasetsByCase={analysisResults.map(analysisResult => {
            return analysisResult?.figures.multi || []
          })}
          defaultPrimaryOutput="emissions by power type"
          chartOptions={chartOptions({ xAxisStep: 10 })}
          colors={seriesColors}
          order={seriesOrder}
          display={display}
        />
      </Accordion>
      <Accordion title="Hourly Results" defaultOpen={true} indentContent={false} stickyHeader={true}>
        <FigureSet figureSet={figureSet} defaultInputs={{ year: "2035" }} />
      </Accordion>
    </>
  );
}

const PowerSystem = (): JSX.Element => {

  const { comparisonCases } = React.useContext(ModuleStateContext)

  return (
    <Layout
      secondCol={[
        <Figures key="figures" />
      ]}
    >
      <ComparisonRow
        sidebar={<></>}
        content={comparisonCases?.map((comparisonCase, comparisonIndex) => {
          return (
            <div key={comparisonCase.id}>
              <PowerUserInputsHandler comparisonIndex={comparisonIndex} />
            </div>
          )
        })}
      />
    </Layout>
  );
};

export default PowerSystem;
