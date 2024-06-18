const fs = require("fs");
const csv = require("fast-csv");
const { isLeapYear } = require("date-fns");
const {
  datesToIgnore,
  balancingAuthorities,
  analysisYears,
} = require("./constants");

exports.usDailyDemandAndGen = (csvFilePaths, outputFilePath) => {
  const promises = csvFilePaths.map((path) => {
    return new Promise((resolve) => {
      const data = {};
      csv
        .parseFile(path, { headers: true })
        .on("data", (row) => {
          if (
            !balancingAuthorities.includes(row["Balancing Authority"]) ||
            datesToIgnore.includes(row["Date"])
          ) {
            return;
          }

          if (!data[row["Date"]]) {
            data[row["Date"]] = {
              demand: 0,
              generation: 0,
            };
          }

          if (
            !Number.isNaN(parseInt(row["Demand (MW)"].replace(",", ""), 10))
          ) {
            data[row["Date"]] = {
              ...data[row["Date"]],
              demand:
                data[row["Date"]].demand +
                parseInt(row["Demand (MW)"].replace(",", ""), 10),
            };
          }
          if (
            !Number.isNaN(
              parseInt(row["Net Generation (MW)"].replace(",", ""), 10)
            )
          ) {
            data[row["Date"]] = {
              ...data[row["Date"]],
              generation:
                data[row["Date"]].generation +
                parseInt(row["Net Generation (MW)"].replace(",", ""), 10),
            };
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

    csvStream.write([
      "Date",
      "Summed Demand (MW)",
      "Summed Net Generation (MW)",
    ]);
    results.forEach((result) => {
      Object.keys(result).forEach((date) => {
        const [month, day, year] = date.split("/");
        const dateObj = new Date(
          parseInt(`20${year}`, 10),
          parseInt(month, 10) - 1,
          parseInt(day, 10)
        );
        // if it's the first of march in a non-leap year, push null before the value
        if (!isLeapYear(dateObj) && month === "3" && day === "1") {
          // add a null value before 3/1 == empty value for 2/29 for non-leap years
          csvStream.write([`2/29/${year}`, null, null]);
        }
        csvStream.write([date, result[date].demand, result[date].generation]);
      });
    });

    csvStream.end();
  });
};
