const fs = require("fs");
const csv = require("fast-csv");

exports.aggregateCovidCases = (filePath, outputPath) => {
  const promise = new Promise((resolve) => {
    const data = {};
    csv
      .parseFile(filePath, { headers: true })
      .on("data", (row) => {
        if (data[row["date"]] === undefined) {
          data[row["date"]] = { cases: 0, deaths: 0 };
        }
        if (!Number.isNaN(parseInt(row["cases"].replace(",", ""), 10))) {
          data[row["date"]] = {
            ...data[row["date"]],
            cases:
              data[row["date"]].cases +
              parseInt(row["cases"].replace(",", ""), 10),
          };
        }
        if (!Number.isNaN(parseInt(row["deaths"].replace(",", ""), 10))) {
          data[row["date"]] = {
            ...data[row["date"]],
            deaths:
              data[row["date"]].deaths +
              parseInt(row["deaths"].replace(",", ""), 10),
          };
        }
      })
      .on("end", () => {
        resolve(data);
      });
  });

  return promise.then((result) => {
    const csvStream = csv.format({ headers: true });
    const writableStream = fs.createWriteStream(outputPath);

    csvStream.pipe(writableStream);
    csvStream.write(["Date", "Cases", "Deaths"]);

    // the data begins on Jan 21, but we need to fill in empty rows
    // for the preceding three weeks, because the graphing library needs
    // the series to have as many data points as the set it's being compared
    // to, which begins Jan 1
    // Array(20)
    //   .fill()
    //   .map((_, idx) => idx + 1)
    //   .forEach((val) => {
    //     if (`${val}`.length === 1) {
    //       // format single digit dates
    //       // with leading zero for consistency
    //       val = `0${val}`;
    //     }
    //     csvStream.write([`01/${val}/2020`, 0, 0]);
    //   });

    Object.keys(result).forEach((key) => {
      const [year, month, day] = key.split("-");
      const today = new Date();
      const currentYear = today.getFullYear();
      if (year < currentYear) return;
      csvStream.write([
        `${month}/${day}/${year}`,
        result[key].cases,
        result[key].deaths,
      ]);
    });

    csvStream.end();
  });
};
