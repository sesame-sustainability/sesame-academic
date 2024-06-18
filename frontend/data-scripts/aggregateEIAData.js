const fs = require("fs");
const csv = require("fast-csv");
const { balancingAuthorities } = require("./constants");

exports.aggregateEIAData = (csvFilePaths, outputFilePath) => {
  const promises = csvFilePaths.map((path) => {
    return new Promise((resolve) => {
      const data = {};
      return csv
        .parseFile(path, { headers: true })
        .on("data", (row) => {
          // handle both e.g. 20 and 2020 formats for year
          let [day, month, year] = row["Data Date"].split("/");
          if (year.length === 4) {
            year = year.slice(-2);
          }

          if (!balancingAuthorities.includes(row["Balancing Authority"])) {
            return;
          }

          const ba = row["Balancing Authority"];
          const date = `${day.charAt(0) === "0" ? day.charAt(1) : day}/${
            month.charAt(0) === "0" ? month.charAt(1) : month
          }/${year}`;

          const demand = parseInt(row["Demand (MW)"].replace(",", ""), 10);
          const netGen = parseInt(
            row["Net Generation (MW)"].replace(",", ""),
            10
          );
          const totalInterchange = parseInt(
            row["Total Interchange (MW)"].replace(",", ""),
            10
          );

          if (data[date] === undefined) {
            data[date] = {};
          }
          if (data[date][ba] === undefined) {
            data[date][ba] = {
              netGen: 0,
              demand: 0,
              totalInterchange: 0,
            };
          }
          data[date][ba] = {
            netGen:
              data[date][ba].netGen + (!Number.isNaN(netGen) ? netGen : 0),
            demand:
              data[date][ba].demand + (!Number.isNaN(demand) ? demand : 0),
            totalInterchange:
              data[date][ba].totalInterchange +
              (!Number.isNaN(totalInterchange) ? totalInterchange : 0),
          };
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
    csvStream.write([
      "Date",
      "Balancing Authority",
      "Demand (MW)",
      "Net Generation (MW)",
      "Total Interchange (MW)",
    ]);

    results.forEach((result) => {
      Object.keys(result).forEach((date) => {
        const balancingAuthorities = Object.keys(result[date]);

        balancingAuthorities.forEach((balancingAuthority) => {
          csvStream.write([
            date,
            balancingAuthority,
            result[date][balancingAuthority].demand,
            result[date][balancingAuthority].netGen,
            result[date][balancingAuthority].totalInterchange,
          ]);
        });
      });
    });

    csvStream.end();
  });
};
