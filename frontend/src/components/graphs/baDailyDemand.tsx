import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

import * as Styles from "../styles";
import { useDashboardData } from "../../hooks/useDashboardData";
import { dateStringtoUTC } from "../../utils";
import {
  balancingAreas,
  balancingAreasDisplay,
  colors,
  bodyFontFamily,
} from "../../utils/constants";

const colorMap = {
  CISO: colors.teal["500"],
  ERCO: colors.green["500"],
  SWPP: colors.blue["500"],
  MISO: colors.red["500"],
  PJM: colors.purple["500"],
  NYIS: colors.yellow["500"],
  ISNE: colors.orange["500"],
  FPL: colors.indigo["500"],
};

const filterData = (rawData: DataPoint[]) => {
  return balancingAreas.map((name) => {
    const data = rawData
      .filter(
        ({ node: { Balancing_Authority } }) => name === Balancing_Authority
      )
      .map(({ node: { Demand__MW_, Date } }) => [
        dateStringtoUTC(Date),
        parseInt(Demand__MW_, 10) < 90000 ? null : parseInt(Demand__MW_, 10),
      ]);
    return {
      name: balancingAreasDisplay[name].short,
      data,
      color: colorMap[name],
      connectNulls: true,
      animation: false,
    };
  });
};

const BADailyDemand = (): JSX.Element => {
  const { allEiaData } = useDashboardData();
  const data = filterData(allEiaData);
  const options = {
    chart: {
      zoomType: "x",
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
    },
    title: {
      text: "Daily electricity demand based on balancing authority",
      margin: 50,
      y: 30,
    },
    series: data,
    xAxis: {
      type: "datetime",
    },
    yAxis: {
      title: {
        text: "Demand (MWh)",
      },
    },
    tooltip: {
      crosshairs: true,
      shared: true,
    },
    credits: {
      text: "Source: EIA-930",
      href: 'javascript:window.open("https://www.eia.gov/realtime_grid/#/status?end=20200529T07", "_blank");void(0);',
      style: {
        fontSize: "12px",
      },
    },
  };

  return (
    <>
      <HighchartsReact highcharts={Highcharts} options={options} />
      <Styles.ClickToZoom />
    </>
  );
};

export default BADailyDemand;
