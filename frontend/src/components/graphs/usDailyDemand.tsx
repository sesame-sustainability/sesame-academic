import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

import { useDashboardData } from "../../hooks/useDashboardData";
import {
  colors,
  responsive,
  analysisYears,
  bodyFontFamily,
  dateTimeLabelFormats,
} from "../../utils/constants";
import * as Styles from "../styles";

type DemandOrGeneration = "Demand__MW_" | "Net_Generation__MW_";

const colorMap = {
  2016: colors.green["400"],
  2017: colors.blue["500"],
  2018: colors.red["400"],
  2019: colors.purple["500"],
  2020: colors.yellow["500"],
  2021: colors.indigo["500"],
};

function generateSeries(data: (string | number | null)[][]) {
  const series: {
    name: "2016" | "2017" | "2018" | "2019" | "2020" | "2021";
    data: (number | null)[];
    color: string;
  }[] = analysisYears.map((year) => ({
    name: year,
    data: [],
    color: colorMap[year],
  }));
  for (const [key, value] of Object.values(data)) {
    if (!key) return [];
    analysisYears.forEach((analysisYear) => {
      const _year = analysisYear.replace("20", "");
      if (`${key}`.split("/")[2] === _year) {
        const dataArray = series.find((item) => item.name === analysisYear);
        if (typeof dataArray !== "undefined") {
          if (value && value !== 0) {
            if (typeof value === "number") {
              dataArray.data.push(value);
            } else if (typeof value === "string") {
              dataArray.data.push(parseInt(value, 10));
            }
          } else {
            dataArray.data.push(null);
          }
        }
      }
    });
  }
  return series;
}

const USDailyDemand = (): JSX.Element => {
  const { demand, netGen } = useDashboardData();
  const [demandSeries] = React.useState(generateSeries(demand));
  const [netGenerationSeries] = React.useState(generateSeries(netGen));
  const [toggleDemandNetGen, setToggleDemandNetGen] =
    React.useState<DemandOrGeneration>("Demand__MW_");

  const options = {
    chart: {
      zoomType: "x",
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
    },
    title: {
      text:
        toggleDemandNetGen === "Demand__MW_"
          ? "U.S. daily electricity demand"
          : "U.S. daily electricity generation",
      margin: 50,
      y: 30,
    },
    plotOptions: {
      series: {
        pointStart: Date.UTC(2016, 0, 1),
        pointInterval: 24 * 3600 * 1000, // one day in ms
      },
    },
    yAxis: {
      title: {
        text:
          toggleDemandNetGen === "Demand__MW_"
            ? "Daily demand (MWh)"
            : "Daily generation (MWh)",
      },
    },
    tooltip: {
      shared: true,
      crosshairs: true,
      dateTimeLabelFormats: {
        day: "%B %e",
      },
    },
    responsive,
    series:
      toggleDemandNetGen === "Demand__MW_" ? demandSeries : netGenerationSeries,
    xAxis: {
      minPadding: "0.02",
      type: "datetime",
      showLastLabel: false,
      dateTimeLabelFormats,
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
      <Styles.GraphSelect>
        <Styles.Select
          value={toggleDemandNetGen}
          style={{
            backgroundColor: "white",
          }}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            setToggleDemandNetGen(e.target.value as DemandOrGeneration);
          }}
        >
          <option value="Demand__MW_">Demand</option>
          <option value="Net_Generation__MW_">Generation</option>
        </Styles.Select>
      </Styles.GraphSelect>
      <HighchartsReact
        highcharts={Highcharts}
        options={JSON.parse(JSON.stringify(options))}
      />
      <Styles.ClickToZoom />
    </>
  );
};

export default USDailyDemand;
