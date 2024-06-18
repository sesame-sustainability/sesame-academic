const fs = require("fs");
const fetch = require("node-fetch");

exports.downloadCovidData = (outputFilePath) => {
  return new Promise((resolve) => {
    (async () => {
      const response = await fetch(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
      );

      const data = await response.text();
      const file = fs.createWriteStream(
        `${outputFilePath}/us-counties_historical.csv`
      );

      file.write(data);
      file.end();
      resolve();
    })();
  });
};
