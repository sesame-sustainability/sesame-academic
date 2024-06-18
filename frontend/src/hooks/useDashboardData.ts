import { useStaticQuery, graphql } from "gatsby";
import { colors } from "../utils/constants";
import { dateStringtoUTC } from "../utils";

export const usePeakEIASeries = (): {
  year2020: {
    name: string;
    data: number[][];
    animation: boolean;
  };
  allAveraged: {
    name: string;
    data: number[][];
    animation: boolean;
    tooltip: {
      dateTimeLabelFormats: {
        day: string;
      };
    };
  };
} => {
  const { averagedData, dailyPeakData } = useDashboardData();
  const year2020 = {
    name: "2021",
    data: dailyPeakData,
    animation: false,
  };
  const allAveraged = {
    name: "2016-2020",
    data: averagedData,
    animation: false,
    tooltip: {
      dateTimeLabelFormats: {
        day: "%A",
      },
    },
  };
  return { year2020, allAveraged };
};

export const useAvgTotalSeries = (): {
  color: string;
  zIndex: number;
  name: string;
  data: number[][];
  animation: boolean;
  tooltip?: {
    dateTimeLabelFormats: {
      day: string;
    };
  };
}[] => {
  const { NUM_POINTS_TO_DISPLAY, avgDates, demand2020, totalAvgDemand } =
    useDashboardData();
  const avgTotalSeries = [
    {
      color: colors.green["400"],
      zIndex: 1,
      name: "2021",
      data: demand2020,
      animation: false,
    },
    {
      color: colors.indigo["400"],
      zIndex: 1,
      name: "2016-2020",
      data: totalAvgDemand
        .slice(0, NUM_POINTS_TO_DISPLAY)
        .map(({ node: { Aggregated_and_averaged_over_4_years } }, index) => {
          return [
            avgDates[index],
            parseInt(Aggregated_and_averaged_over_4_years, 10),
          ];
        }),
      animation: false,
      tooltip: {
        dateTimeLabelFormats: {
          day: "%A",
        },
      },
    },
  ];
  return avgTotalSeries;
};
export const useDashboardData = (): {
  demand: (string | number | null)[][];
  netGen: (string | number | null)[][];
  allEiaData: DataPoint[];
  allCovidCases: { nodes: CovidCaseNode[] };
  totalAvgDemand: {
    node: {
      Aggregated_and_averaged_over_4_years: string;
    };
  }[];
  NUM_POINTS_TO_DISPLAY: number;
  demand2020: number[][];
  dailyPeakData: number[][];
  averagedData: number[][];
  avgDates: number[];
  lastUpdated: string;
} => {
  const {
    allSummedDemand,
    allSummedNetGen,
    allEia20162018,
    allEia20182020,
    allTotalDemand2020Csv,
    allCovidCasesCsv: allCovidCases,
    allTotalAvgDemand20162019Csv: { edges: totalAvgDemand },
    allPeakEia2020,
    allAvgPeakEia,
    site: {
      siteMetadata: { lastUpdated },
    },
  }: {
    allSummedDemand: { nodes: { Summed_Demand__MW_: string; Date: string }[] };
    allSummedNetGen: {
      nodes: { Summed_Net_Generation__MW_: string; Date: string }[];
    };
    allEia20162018: Edges;
    allEia20182020: Edges;
    allCovidCasesCsv: {
      nodes: CovidCaseNode[];
    };
    allTotalDemand2020Csv: {
      edges: {
        node: { Data_Date: string; Summed_Demand__MW_: string };
      }[];
    };
    allTotalAvgDemand20162019Csv: {
      edges: {
        node: { Aggregated_and_averaged_over_4_years: string };
      }[];
    };
    allPeakEia2020: PeakEIA;
    allAvgPeakEia: AverageDailyPeak;
    site: {
      siteMetadata: {
        lastUpdated: string;
      };
    };
  } = useStaticQuery(graphql`
    query AllEIAData {
      allSummedDemand: allDemandGenCsv {
        nodes {
          Date
          Summed_Demand__MW_
        }
      }
      allSummedNetGen: allDemandGenCsv {
        nodes {
          Date
          Summed_Net_Generation__MW_
        }
      }
      allEia20162018: allEia20162018JunCsv(
        filter: {
          Balancing_Authority: {
            in: ["CISO", "FPL", "MISO", "NYIS", "SWPP", "ERCO"]
          }
        }
      ) {
        edges {
          node {
            Date
            Demand__MW_
            Net_Generation__MW_
            Balancing_Authority
            Total_Interchange__MW_
          }
        }
      }
      allEia20182020: allEia2018JunCurrentCsv(
        filter: {
          Balancing_Authority: {
            in: ["CISO", "FPL", "MISO", "NYIS", "SWPP", "ERCO"]
          }
        }
      ) {
        edges {
          node {
            Date
            Demand__MW_
            Net_Generation__MW_
            Balancing_Authority
            Total_Interchange__MW_
          }
        }
      }
      allPeakEia2020: allPeakEia930Balance2020Csv {
        edges {
          node {
            Summed_peak_hourly_Demand__MW_
            Data_Date
          }
        }
      }
      allAvgPeakEia: allAverageDailyPeakCsv {
        nodes {
          Avg_daily_peak
        }
      }
      allTotalAvgDemand20162019Csv {
        edges {
          node {
            Aggregated_and_averaged_over_4_years
          }
        }
      }
      allTotalDemand2020Csv {
        edges {
          node {
            Data_Date
            Summed_Demand__MW_
          }
        }
      }
      allCovidCasesCsv {
        nodes {
          Cases
          Date
        }
      }
      site {
        siteMetadata {
          lastUpdated
        }
      }
    }
  `);

  const dates: number[] = [];
  const avgDates: number[] = [];
  const NUM_POINTS_TO_DISPLAY = allTotalDemand2020Csv.edges.length;

  const demand2020 = allTotalDemand2020Csv.edges.map(
    ({ node: { Summed_Demand__MW_, Data_Date } }) => {
      avgDates.push(dateStringtoUTC(Data_Date));
      return [dateStringtoUTC(Data_Date), parseInt(Summed_Demand__MW_, 10)];
    }
  );
  const dailyPeakData = allPeakEia2020.edges
    .slice(0, NUM_POINTS_TO_DISPLAY)
    .map(({ node: { Summed_peak_hourly_Demand__MW_, Data_Date } }) => {
      dates.push(dateStringtoUTC(Data_Date));
      return [
        dateStringtoUTC(Data_Date),
        parseInt(Summed_peak_hourly_Demand__MW_, 10),
      ];
    });
  const averagedData = allAvgPeakEia.nodes
    .slice(0, NUM_POINTS_TO_DISPLAY)
    .map(({ Avg_daily_peak }, index) => {
      return [dates[index], parseInt(Avg_daily_peak, 10)];
    });
  const allEiaData = [...allEia20162018.edges, ...allEia20182020.edges];

  const demand = allSummedDemand.nodes.map(({ Summed_Demand__MW_, Date }) => [
    Date,
    parseInt(Summed_Demand__MW_, 10) || null,
  ]);

  const netGen = allSummedNetGen.nodes.map(
    ({ Summed_Net_Generation__MW_, Date }) => [
      Date,
      parseInt(Summed_Net_Generation__MW_, 10) || null,
    ]
  );

  return {
    demand,
    netGen,
    allEiaData,
    allCovidCases,
    totalAvgDemand,
    NUM_POINTS_TO_DISPLAY,
    demand2020,
    avgDates,
    dailyPeakData,
    averagedData,
    lastUpdated,
  };
};
