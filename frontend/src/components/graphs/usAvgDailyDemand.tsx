import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

import {
  useDashboardData,
  useAvgTotalSeries,
  usePeakEIASeries,
} from "../../hooks/useDashboardData";
import * as Styles from "../../components/styles";
import {
  dateTimeLabelFormats,
  colors,
  bodyFontFamily,
} from "../../utils/constants";
import { isBrowser } from "../../utils";

const USAvgDailyDemand = (): JSX.Element => {
  const { NUM_POINTS_TO_DISPLAY, avgDates, allCovidCases } = useDashboardData();
  const avgTotalSeries = useAvgTotalSeries();
  const { year2020, allAveraged } = usePeakEIASeries();

  const [totalOrPeak, setTotalOrPeak] =
    React.useState<"total" | "peak">("total");
  const avgPeakSeriesOpts = React.useMemo(() => {
    const covidSeries = {
      name: "Cases",
      animation: false,
      yAxis: 1,
      type: "column",
      color: colors.orange["300"],
      data: allCovidCases.nodes
        .slice(0, NUM_POINTS_TO_DISPLAY)
        .map(({ Cases }, index) => [avgDates[index], parseInt(Cases, 10)]),
    };

    if (totalOrPeak === "total") {
      return [...avgTotalSeries, covidSeries];
    }
    return [year2020, allAveraged, covidSeries];
  }, [
    avgTotalSeries,
    allAveraged,
    year2020,
    totalOrPeak,
    avgDates,
    allCovidCases.nodes,
    NUM_POINTS_TO_DISPLAY,
  ]);

  const avgTotalOpts = {
    title: {
      text:
        totalOrPeak === "total"
          ? "U.S. average daily electricity demand"
          : "U.S. daily peak electricity demand",
      margin: 50,
      y: 30,
    },
    chart: {
      type: "line",
      zoomType: "x",
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
    },
    responsive: {
      rules: [
        {
          condition: {
            maxWidth: 500,
          },
          chartOptions: {
            title: {
              y: 80,
              margin: 90,
            },
          },
        },
      ],
    },
    tooltip: {
      crosshairs: true,
      shared: true,
    },
    yAxis: [
      {
        title: {
          text: totalOrPeak === "total" ? "Total demand (MWh)" : "Peak (MW)",
        },
      },
      {
        title: {
          text: "COVID-19 Cases",
        },
        opposite: true,
      },
    ],
    series: avgPeakSeriesOpts,
    xAxis: {
      type: "datetime",
      dateTimeLabelFormats,
    },
    credits: {
      text: "Source: EIA-930 and CSBS",
      href: 'javascript:window.open("https://www.csbs.org/information-covid-19-coronavirus", "_blank");void(0);',
      style: {
        fontSize: "12px",
      },
    },
  };
  return (
    <Styles.ChartWrapper>
      <Styles.GraphSelect>
        <Styles.Select
          value={totalOrPeak}
          style={{
            backgroundColor: "white",
          }}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            setTotalOrPeak(e.target.value as "total" | "peak");
          }}
        >
          <option value="total">Total</option>
          <option value="peak">Peak</option>
        </Styles.Select>
      </Styles.GraphSelect>

      {isBrowser() && (
        <>
          <HighchartsReact highcharts={Highcharts} options={avgTotalOpts} />
          <Styles.ClickToZoom />
        </>
      )}
    </Styles.ChartWrapper>
  );
};

export default USAvgDailyDemand;
