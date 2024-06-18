const fs = require("fs");
const csv = require("fast-csv");

exports.avgDailyDemandPeak = (csvFilePaths, outputPath) => {
  const promises = csvFilePaths.map((path) => {
    return new Promise((resolve) => {
      const data = {};
      csv
        .parseFile(path, { headers: true })
        .on("data", (row) => {
          if (!data[row["Local Time at End of Hour"]]) {
            data[row["Local Time at End of Hour"]] = {
              demand: 0,
              dataDate: row["Data Date"],
            };
          }
          if (
            !Number.isNaN(parseInt(row["Demand (MW)"].replace(",", ""), 10))
          ) {
            data[row["Local Time at End of Hour"]] = {
              demand:
                data[row["Local Time at End of Hour"]].demand +
                parseInt(row["Demand (MW)"].replace(",", ""), 10),
              dataDate: row["Data Date"],
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
    const writableStream = fs.createWriteStream(outputPath);

    csvStream.pipe(writableStream);
    csvStream.write(["Data Date", "Summed peak hourly Demand (MW)"]);

    const peakHourInDay = {};

    results.forEach((result) => {
      Object.keys(result).forEach((key) => {
        const currentDemand = parseInt(result[key].demand, 10);
        const currentDemandIsNumber = !Number.isNaN(currentDemand);
        const existingValue = peakHourInDay[result[key].dataDate];

        if (!existingValue && currentDemandIsNumber) {
          peakHourInDay[result[key].dataDate] = currentDemand;
        } else if (
          currentDemandIsNumber &&
          existingValue &&
          currentDemand > existingValue
        ) {
          peakHourInDay[result[key].dataDate] = currentDemand;
        }
      });
    });

    Object.keys(peakHourInDay).forEach((key) => {
      if (peakHourInDay[key] === 0) return;
      csvStream.write([key, peakHourInDay[key]]);
    });

    csvStream.end();
  });
};
