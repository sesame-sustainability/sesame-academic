import React from "react";
import { graphql, useStaticQuery } from "gatsby";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import * as Styles from "../styles";
import { dateStringtoUTC } from "../../utils";
import {
  responsive,
  balancingAreas,
  balancingAreasDisplay,
  bodyFontFamily,
  colors,
} from "../../utils/constants";

interface HourlyTotalsEdge {
  edges: { node: { Averaged_Demand__MwH_: string; Date?: string } }[];
}

const HourlyTotalsGraph = ({
  onBAChange,
}: {
  onBAChange: (delta: Record<string, string>) => void;
}): JSX.Element => {
  const [selectedBA, setSelectedBA] = React.useState<BalancingArea>("CISO");
  const {
    CISO,
    ERCO,
    SWPP,
    MISO,
    PJM,
    NYIS,
    ISNE,
    FPL,
    CISO2020,
    ERCO2020,
    SWPP2020,
    MISO2020,
    PJM2020,
    NYIS2020,
    ISNE2020,
    FPL2020,
  } = useStaticQuery<{
    CISO: HourlyTotalsEdge;
    ERCO: HourlyTotalsEdge;
    SWPP: HourlyTotalsEdge;
    MISO: HourlyTotalsEdge;
    PJM: HourlyTotalsEdge;
    NYIS: HourlyTotalsEdge;
    ISNE: HourlyTotalsEdge;
    FPL: HourlyTotalsEdge;
    CISO2020: HourlyTotalsEdge;
    ERCO2020: HourlyTotalsEdge;
    SWPP2020: HourlyTotalsEdge;
    MISO2020: HourlyTotalsEdge;
    PJM2020: HourlyTotalsEdge;
    NYIS2020: HourlyTotalsEdge;
    ISNE2020: HourlyTotalsEdge;
    FPL2020: HourlyTotalsEdge;
  }>(graphql`
    query HourlyTotalsQuery {
      CISO: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "CISO" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      ERCO: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "ERCO" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      SWPP: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "SWPP" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      MISO: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "MISO" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      PJM: allHourlyTotalsCsv(filter: { Balancing_Authority: { eq: "PJM" } }) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      NYIS: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "NYIS" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      ISNE: allHourlyTotalsCsv(
        filter: { Balancing_Authority: { eq: "ISNE" } }
      ) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      FPL: allHourlyTotalsCsv(filter: { Balancing_Authority: { eq: "FPL" } }) {
        edges {
          node {
            Averaged_Demand__MwH_
          }
        }
      }
      CISO2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "CISO" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      ERCO2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "ERCO" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      SWPP2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "SWPP" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      MISO2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "MISO" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      PJM2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "PJM" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      NYIS2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "NYIS" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      ISNE2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "ISNE" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
      FPL2020: allHourlyTotals2020Csv(
        filter: { Balancing_Authority: { eq: "FPL" } }
      ) {
        edges {
          node {
            Date
            Averaged_Demand__MwH_
          }
        }
      }
    }
  `);

  const dates: number[] = React.useMemo(() => [], []);
  const CISOData = React.useMemo(
    () =>
      CISO2020.edges.map(({ node }) => {
        if (typeof node.Date === "undefined") return;
        const [date, , , time] = node.Date.split(" ");
        const UTCDate = dateStringtoUTC(date, time === "24" ? "0" : time);
        dates.push(UTCDate);
        return [UTCDate, parseInt(node.Averaged_Demand__MwH_, 10)];
      }),
    [CISO2020.edges, dates]
  );
  const ERCOData = React.useMemo(
    () =>
      ERCO2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [ERCO2020.edges, dates]
  );
  const SWPPData = React.useMemo(
    () =>
      SWPP2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [SWPP2020.edges, dates]
  );
  const MISOData = React.useMemo(
    () =>
      MISO2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [MISO2020.edges, dates]
  );
  const PJMData = React.useMemo(
    () =>
      PJM2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [PJM2020.edges, dates]
  );
  const NYISData = React.useMemo(
    () =>
      NYIS2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [NYIS2020.edges, dates]
  );
  const ISNEData = React.useMemo(
    () =>
      ISNE2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [ISNE2020.edges, dates]
  );
  const FPLData = React.useMemo(
    () =>
      FPL2020.edges.map(({ node: { Averaged_Demand__MwH_ } }, index) => {
        return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
      }),
    [FPL2020.edges, dates]
  );

  const BalancingAuthoritiesData = React.useMemo(
    () => ({
      CISO: {
        data: CISO,
        hourlyData: CISOData,
      },
      ERCO: {
        data: ERCO,
        hourlyData: ERCOData,
      },
      SWPP: {
        data: SWPP,
        hourlyData: SWPPData,
      },
      MISO: {
        data: MISO,
        hourlyData: MISOData,
      },
      PJM: {
        data: PJM,
        hourlyData: PJMData,
      },
      NYIS: {
        data: NYIS,
        hourlyData: NYISData,
      },
      ISNE: {
        data: ISNE,
        hourlyData: ISNEData,
      },
      FPL: {
        data: FPL,
        hourlyData: FPLData,
      },
    }),
    [
      CISO,
      CISOData,
      ERCO,
      ERCOData,
      FPL,
      FPLData,
      ISNE,
      ISNEData,
      MISO,
      MISOData,
      NYIS,
      NYISData,
      PJM,
      PJMData,
      SWPP,
      SWPPData,
    ]
  );

  const options = {
    chart: {
      zoomType: "x",
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
    },
    tooltip: {
      crosshairs: true,
      shared: true,
    },
    title: {
      text: "Hourly electricity load profile",
      margin: 50,
      y: 30,
    },
    xAxis: {
      type: "datetime",
    },
    yAxis: {
      title: {
        text: "Demand (MW)",
      },
    },
    responsive,
    series: [
      {
        color: colors.red["400"],
        name: `${balancingAreasDisplay[selectedBA].short} 2020`,
        data: BalancingAuthoritiesData[selectedBA].hourlyData,
        animation: false,
      },
      {
        color: colors.blue["400"],
        name: `${balancingAreasDisplay[selectedBA].short} 2016-2019 average`,
        data: BalancingAuthoritiesData[selectedBA].data.edges
          .slice(0, BalancingAuthoritiesData[selectedBA].hourlyData.length)
          .map(({ node: { Averaged_Demand__MwH_ } }, index) => {
            return [dates[index], parseInt(Averaged_Demand__MwH_, 10)];
          }),
        animation: false,
      },
    ],
    credits: {
      text: "Source: EIA-930",
      href: 'javascript:window.open("https://www.eia.gov/realtime_grid/#/status?end=20200529T07", "_blank");void(0);',
      style: {
        fontSize: "12px",
      },
    },
  };

  const calculateDelta = React.useCallback(
    (BA: BalancingArea) => {
      let total1 = 0;
      let total2 = 0;
      if (!Array.isArray(BalancingAuthoritiesData[BA].hourlyData)) return "";

      BalancingAuthoritiesData[BA].hourlyData.forEach((item) => {
        if (!Array.isArray(item)) return;
        total1 += item[1];
      });

      BalancingAuthoritiesData[BA].data.edges
        .slice(0, BalancingAuthoritiesData[BA].hourlyData.length)
        .forEach(({ node: { Averaged_Demand__MwH_ } }) => {
          total2 += parseInt(Averaged_Demand__MwH_, 0);
        });
      return (((total1 - total2) / total1) * 100).toFixed(2);
    },
    [BalancingAuthoritiesData]
  );

  React.useEffect(() => {
    const allCalculatedDeltas = balancingAreas.reduce((acc, cur) => {
      return { ...acc, [cur]: calculateDelta(cur) };
    }, {});
    onBAChange(allCalculatedDeltas);
  }, [calculateDelta, onBAChange]);

  return (
    <>
      <Styles.GraphSelect>
        <Styles.Select
          style={{
            backgroundColor: "white",
          }}
          value={selectedBA}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            setSelectedBA(e.target.value as BalancingArea);
          }}
        >
          {balancingAreas.map((item) => (
            <option key={`${item}`} value={item}>
              {balancingAreasDisplay[item].short}
            </option>
          ))}
        </Styles.Select>
      </Styles.GraphSelect>
      <HighchartsReact highcharts={Highcharts} options={options} />
      <Styles.ClickToZoom />
    </>
  );
};

export default HourlyTotalsGraph;
