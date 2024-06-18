const fs = require("fs");
const csv = require("fast-csv");
const { firstDates, balancingAuthorities } = require("./constants");

exports.calculateAverageLoadPattern = (csvFilePaths, outputFilePath) => {
  const promises = csvFilePaths.map((path) => {
    return new Promise((resolve) => {
      const data = {};
      return csv
        .parseFile(path, { headers: true })
        .on("data", (row) => {
          // handle both e.g. 20 and 2020 formats for year
          let [month, day, year] = row["Data Date"].split("/");
          if (year.length === 2) {
            year = `20${year}`;
          }

          const [ignoreMonth, ignoreDay] = firstDates[year].split("/");

          if (
            !balancingAuthorities.includes(row["Balancing Authority"]) ||
            parseInt(month) < parseInt(ignoreMonth) ||
            (parseInt(month) === parseInt(ignoreMonth) &&
              parseInt(day) < parseInt(ignoreDay))
          ) {
            return;
          }

          const demand = parseInt(row["Demand (MW)"].replace(",", ""), 10);
          if (data[row["Balancing Authority"]] === undefined) {
            data[row["Balancing Authority"]] = {};
          }
          if (data[row["Balancing Authority"]][year] === undefined) {
            data[row["Balancing Authority"]][year] = {
              [`${row["Local Time at End of Hour"]} ${row["Hour Number"]}`]: !Number.isNaN(
                demand
              )
                ? demand
                : 0,
            };
          }
          if (
            data[row["Balancing Authority"]][year][
              `${row["Local Time at End of Hour"]} ${row["Hour Number"]}`
            ] === undefined
          ) {
            data[row["Balancing Authority"]][year][
              `${row["Local Time at End of Hour"]} ${row["Hour Number"]}`
            ] = !Number.isNaN(demand) ? demand : 0;
          }
        })
        .on("end", function () {
          resolve(data);
        });
    });
  });

  return Promise.all(promises).then((results) => {
    const csvStream = csv.format({ headers: true });
    const writableStream = fs.createWriteStream(outputFilePath);

    csvStream.pipe(writableStream);

    const formattedResults = results.reduce((acc, curr) => {
      const newData = acc;
      Object.keys(curr).forEach((ba) => {
        const [year] = Object.keys(curr[ba]);
        if (newData[year] === undefined) {
          newData[year] = {};
        }
        if (newData[year][ba] === undefined) {
          newData[year][ba] = {};
        }
        newData[year][ba] = { ...newData[year][ba], ...curr[ba][year] };
      });
      return { ...acc, ...newData };
    }, {});

    const NUMBER_OF_YEARS = Object.keys(formattedResults).length;

    if (NUMBER_OF_YEARS === 1) {
      csvStream.write(["Balancing Authority", "Date", "Averaged Demand (MwH)"]);
    } else {
      csvStream.write([
        "Balancing Authority",
        "Index",
        "Averaged Demand (MwH)",
      ]);
    }

    const aggregatedData = {};

    Object.keys(formattedResults).forEach((year) => {
      Object.keys(formattedResults[year]).forEach((ba) => {
        if (aggregatedData[ba] === undefined) {
          aggregatedData[ba] = {};
        }
        Object.keys(formattedResults[year][ba]).forEach((dateTime, index) => {
          let i = index;
          if (NUMBER_OF_YEARS === 1) {
            i = dateTime;
          }
          if (Number.isNaN(formattedResults[year][ba][dateTime])) {
            return;
          }
          if (aggregatedData[ba][i] === undefined) {
            aggregatedData[ba][i] = {
              n: 1,
              val: parseInt(formattedResults[year][ba][dateTime]),
            };
          } else if (parseInt(formattedResults[year][ba][dateTime]) > 0) {
            aggregatedData[ba][i] = {
              n: aggregatedData[ba][i].n + 1,
              val:
                aggregatedData[ba][i].val +
                parseInt(formattedResults[year][ba][dateTime]),
            };
          }
        });
      });
    });

    Object.keys(aggregatedData).forEach((BA) => {
      Object.keys(aggregatedData[BA]).forEach((index) => {
        // here, we divide by the number of non-null values we added together
        // this fixes a bug with SWPP data which is missing 2018 data, so dividing
        // by the number of years results in an erroneous average
        const val = aggregatedData[BA][index].val / aggregatedData[BA][index].n;
        if (val === 0) {
          return;
        }
        csvStream.write([BA, index, val]);
      });
    });

    csvStream.end();
  });
};
