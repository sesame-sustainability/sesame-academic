import React from "react";
import Highcharts from "highcharts";
import HighchartsMore from "highcharts/highcharts-more";
import HighchartsReact from "highcharts-react-official";
import { bodyFontFamily, colors, transparent } from "../utils/constants";
import { formatLabelString, isBrowser } from "../utils";
import * as Styles from "./styles";
import { Toggle } from "./toggle";
import { ChartExportButton } from "./chartExportButton";
import { chartColors, maxBarWidth, Series, valueFormatter } from "./figures";

// HighChartsMore lib is required for error bars
// ...and is a browser-only lib, so it will break the build
// if called on the server
if (isBrowser()) {
  HighchartsMore(Highcharts);
}

const lcaChartColors = {
  'upstream': chartColors.black,
  'midstream': chartColors.indigo_light,
  'process': chartColors.orange,
  'gate': colors.purple['800'],
  'enduse': chartColors.green,
}

export const getLCATEABarChartHeight = ({
  numBars,
  numBarGroups,
  // numSeries = 1,
  isChartStacked,
}: {
  // series: Series[],
  // numSeries: number;
  numBarGroups: number;
  numBars: number;
  isChartStacked: boolean
}) => {
  const legendHeightGuess = 140;
  const barPadding = 8;
  const pixelsPerBar = (isChartStacked ? maxBarWidth : 15) + barPadding;//isChartStacked ? 50 : 25;
  const totalBarGroupPaddingHeight = numBarGroups * 14;
  const chartHeight = (pixelsPerBar * numBars) + legendHeightGuess + totalBarGroupPaddingHeight;
  return chartHeight;
}

export const BAR_CHART_SPACING_BOTTOM = 90;
export const BAR_CHART_LEGEND_Y = 70;

const stageNames = ['Enduse', 'GateToEnduse', 'Process', 'Midstream', 'Upstream']

const PathwayAnalysisGraph = ({
  response,
}: {
  response?: PathwayAnalysisResponse & {
    data: Data[];
  };
}): JSX.Element | null => {

  const [isChartStacked, setIsChartStacked] = React.useState(true);
  const chartRef = React.useRef(null);
  const [title, setTitle] = React.useState('');

  // let title = "";

  const options = React.useMemo(() => {
    const series = [];
    const categories: string[] = [];
    // let title = "";
    let unit = "";
    if (!response)
      return null;
      // return {
      //   chart: {
      //     type: "column",
      //     style: {
      //       fontFamily: bodyFontFamily.join(", "),
      //     },
      //   },
      //   credits: {
      //     enabled: false,
      //   },
      //   title: {
      //     text: "",
      //   },
      // };

    const pathwayData: { name: string; data: number[] }[] = [];

    for (const [key] of Object.entries(response)) {
      if (key === "title") {
        setTitle(String(response[key]));
        // title = response[key];
        // title = `${title}`;
      }
      if (key === "unit") {
        let formattedUnit = response[key];
        // future-proofing for this update: https://github.mit.edu/sesame/sesame-core/commit/a073dbd7bd7deb971376dbc993a36bbaaabd6a32?email_source=notifications&email_token=AAAET43D6ESGIMHNIMZKDD3S2ZWGLA5CNFSM4AABNGRKYY3PNVWWK3TUL52HS4DFVVBW63LNNF2EG33NNVSW45FKMNXW23LFNZ2F62LEZUKPS
        if (response[key] === "kgco2eq" || response[key] === "gco2eq") {
          formattedUnit = "kg CO2eq/kWh";
        }
        unit = formattedUnit;
      }
      if (key === "data") {
        // debugger
        for (const [index, { pathway, ...recordOfStageNamesAndValues }] of Object.entries(
          response[key]
        )) {
          if (typeof pathway === "string") {
            categories.push(pathway);
          }
          for (const stage of stageNames) {
          // for (const [stage, value] of Object.entries(rest)) {
            const colorKey = formatLabelString(stage).split(' ')?.[0].toLowerCase();
            if (!pathwayData?.find((i) => i.name === stage)) {
              pathwayData.push({ name: stage, data: [], color: lcaChartColors[colorKey] });
            }
            const pathwayConfig = pathwayData?.find((i) => i.name === stage);
            const value = recordOfStageNamesAndValues[stage] || 0;
            if (typeof value === "string") return;
            pathwayConfig?.data.push(value);
          }
        }
        series.push(pathwayData.map(item => {
          return { ...item, name: formatLabelString(item.name) };
        }).reverse());
      }
    }

    const numPathways = response?.data?.length || 1;
    const numBars = isChartStacked ? numPathways : pathwayData.map(dataObj => dataObj.data).flat().length;

    
    return {
      chart: {
        type: "bar",
        style: {
          fontFamily: bodyFontFamily.join(", "),
        },
        height: getLCATEABarChartHeight({numBars, numBarGroups: numPathways, isChartStacked}),
        animation: false,
        spacingBottom: BAR_CHART_SPACING_BOTTOM,
      },
      navigation: {
        buttonOptions: {
          enabled: false,
        },
      },
      legend: {
        // layout: "vertical",
        // align: "left",
        // verticalAlign: "middle",
        // itemMarginTop: 1,
        // itemMarginBottom: 3,
        floating: true,
        // reversed: true,
        y: BAR_CHART_LEGEND_Y,
        itemStyle: {
          color: '#555',
          fontWeight: 'normal'
        },
        itemMarginTop: 1,
        itemMarginBottom: 3,
      },
      credits: {
        enabled: false,
      },
      title: {
        text: null,
      },
      xAxis: {
        // categories: series[0].map(serie => serie.name),
        categories,
        // reversed: (isChartStacked ? undefined : true),
        plotLines: new Array(numPathways - 1).fill(null).map((o, index) => ({
          color: '#d1d5db',
          width: 1,
          value: index + 0.5 // Need to set this probably as a var.
        })),
      },
      yAxis: {
        title: {
          text: unit,
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
          }
        },
        reversedStacks: false,
      },
      tooltip: {
        headerFormat: "<b>{point.x}</b><br/>",
        // pointFormat: isChartStacked ? 
        //   "{series.name}: {point.y}<br/>Total: {point.stackTotal}"
        //   :
        //   "{series.name}: {point.y}<br/>",
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
      plotOptions: {
        bar: {
          stacking: isChartStacked ? "normal" : undefined,
          borderWidth: 0,
          maxPointWidth: maxBarWidth,
          pointWidth: isChartStacked ? maxBarWidth : 15,
          groupPadding: 0.15,
          dataLabels: {
            enabled: !isChartStacked,
            color: "#666",
            formatter: function(): string {
              const value = this.y;
              return valueFormatter({value});
            }
          },
        },
      },
      series: isChartStacked ? [...series[0]] : series[0],
    };
  }, [response, isChartStacked]);

  return isBrowser() && options ? (
    <Styles.Col2>
      <div className="relative">
        <Styles.ChartTitle>{title}</Styles.ChartTitle>
        <ChartExportButton chartTitle={title} chartRef={chartRef} />
        <HighchartsReact highcharts={Highcharts} options={options} ref={chartRef} />
        <div className="absolute top-6 left-0">  
          <Toggle label="Stack Bars" value={isChartStacked} setValue={setIsChartStacked} />
        </div>
      </div>
    </Styles.Col2>
  ) : null;
};

export default PathwayAnalysisGraph;
