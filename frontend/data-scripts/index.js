const Listr = require("listr");
const { Observable } = require("rxjs");

// const { calculateAverageLoadPattern } = require(`./calculateAvgLoadPattern`);
const { aggregateCovidCases } = require(`./aggregateCovidCases`);
const { avgDailyDemandTotal } = require(`./avgDailyDemandTotal`);
const { usDailyDemandAndGen } = require(`./usDailyDemandAndGen`);
const { avgDailyDemandPeak } = require(`./avgDailyDemandPeak`);
const { downloadCovidData } = require(`./downloadCovidData`);
const { aggregateEIAData } = require(`./aggregateEIAData`);
const { downloadEIAData } = require(`./downloadEIAData`);

const DATA_DIR = `${__dirname}/bulk-data`;
const OUTPUT_DIR = `${__dirname}/../src/data`;

const tasks = new Listr([
  {
    title: "Download fresh data 💾",
    task: () => {
      const today = new Date();
      const year = today.getFullYear();
      return new Listr([
        {
          title: "Download new COVID-19 case data",
          task: () => {
            return new Observable((observer) => {
              downloadCovidData(DATA_DIR).then(() => observer.complete());
            });
          },
        },
        {
          title: `Download new ${year} EIA data`,
          task: () => {
            return new Observable((observer) => {
              downloadEIAData(DATA_DIR).then(() => observer.complete());
            });
          },
        },
      ]);
    },
  },
  {
    title: "Update aggregated CSVs 📊",
    task: () => {
      return new Listr([
        {
          title: "Generate EIA_2018_Jun_current.csv",
          task: () => {
            return new Observable((observer) => {
              aggregateEIAData(
                [
                  `${DATA_DIR}/EIA930_BALANCE_2018_Jul_Dec.csv`,
                  `${DATA_DIR}/EIA930_BALANCE_2019_Jan_Jun.csv`,
                  `${DATA_DIR}/EIA930_BALANCE_2019_Jul_Dec.csv`,
                  `${DATA_DIR}/EIA930_BALANCE_2020_Jan_Jun.csv`,
                  `${DATA_DIR}/EIA930_BALANCE_2020_Jul_Dec.csv`,
                  `${DATA_DIR}/EIA930_BALANCE_2021_Jan_Jun.csv`,
                ],
                `${OUTPUT_DIR}/EIA_2018_Jun_current.csv`
              ).then(() => observer.complete());
            });
          },
        },
        {
          title: "Generate COVID_CASES.csv",
          task: () => {
            return new Observable((observer) => {
              aggregateCovidCases(
                `${DATA_DIR}/us-counties_historical.csv`,
                `${OUTPUT_DIR}/COVID_CASES.csv`
              ).then(() => observer.complete());
            });
          },
        },
        {
          title: "Generate TOTAL_DEMAND_2020.csv",
          task: () => {
            return new Observable((observer) => {
              avgDailyDemandTotal(
                [`${DATA_DIR}/EIA930_BALANCE_2021_Jan_Jun.csv`],
                `${OUTPUT_DIR}/TOTAL_DEMAND_2020.csv`
              ).then(() => observer.complete());
            });
          },
        },
        {
          title: "Generate PEAK_EIA930_BALANCE_2020.csv",
          task: () => {
            return new Observable((observer) => {
              avgDailyDemandPeak(
                [`${DATA_DIR}/EIA930_BALANCE_2021_Jan_Jun.csv`],
                `${OUTPUT_DIR}/PEAK_EIA930_BALANCE_2020.csv`
              ).then(() => observer.complete());
            });
          },
        },
        {
          title: "Format US Daily Demand and Generation data",
          task: () => {
            return new Observable((observer) => {
              usDailyDemandAndGen(
                [
                  `${OUTPUT_DIR}/EIA_2016_2018_Jun.csv`,
                  `${OUTPUT_DIR}/EIA_2018_Jun_current.csv`,
                ],
                `${OUTPUT_DIR}/DEMAND_GEN.csv`
              ).then(() => observer.complete());
            });
          },
        },
      ]);
    },
  },
]);

tasks.run().catch((err) => {
  console.error(err);
});
