const fs = require("fs");
const csv = require("fast-csv");
const { datesToIgnore } = require("./constants");

exports.avgDailyDemandTotal = (csvFilePaths, outputFilePath) => {
  const promises = csvFilePaths.map((path) => {
    return new Promise((resolve) => {
      const data = {};
      csv
        .parseFile(path, { headers: true })
        .on("data", (row) => {
          if (datesToIgnore.includes(row["Data Date"])) {
            return;
          }
          if (!data[row["Data Date"]]) {
            data[row["Data Date"]] = 0;
          }
          if (
            !Number.isNaN(parseInt(row["Demand (MW)"].replace(",", ""), 10))
          ) {
            data[row["Data Date"]] =
              data[row["Data Date"]] +
              parseInt(row["Demand (MW)"].replace(",", ""), 10);
          }
        })
        .on("end", () => {
          resolve(data);
        });
    });
  });

  return Promise.all(promises).then((results) => {
    const csvStream = csv.format({ headers: true });
    const writableStream = fs.createWriteStream(outputFilePath);

    csvStream.pipe(writableStream);
    // if it's 1-2 CSVs, we're just processing one year aka 2020
    if (results.length < 3) {
      csvStream.write(["Data Date", "Summed Demand (MW)"]);
      results.forEach((result) => {
        Object.keys(result).forEach((date) => {
          if (result[date] === 0) return;
          csvStream.write([date, result[date]]);
        });
      });
    } else {
      csvStream.write(["Aggregated and averaged over 4 years"]);
      const data = {};

      results.forEach((result) => {
        Object.keys(result).forEach((date) => {
          const [, , year] = date.trim().split("/");
          data[year] = { ...data[year], [date]: result[date] };
        });
      });

      const totals = [];
      Object.keys(data).forEach((year) => {
        Object.values(data[year]).forEach((val, i) => {
          if (!totals[i]) {
            totals[i] = 0;
          }
          totals[i] += val;
        });
      });

      // we are calculating an average for four years,
      // 2016-2019
      const NUM_YEARS = Object.keys(data).length;

      totals.forEach((val) => {
        csvStream.write([val / NUM_YEARS]);
      });
    }

    csvStream.end();
  });
};
