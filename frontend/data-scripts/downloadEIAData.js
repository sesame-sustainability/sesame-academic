const fs = require("fs");
const fetch = require("node-fetch");

exports.downloadEIAData = (outputFilePath) => {
  return new Promise((resolve) => {
    (async () => {
      const today = new Date();
      const month = today.getMonth(); // month is zero indexed
      const year = today.getFullYear();
      const formattedMonth = month >= 0 && month <= 5 ? "Jan_Jun" : "Jul_Dec";
      const filename = `EIA930_BALANCE_${year}_${formattedMonth}.csv`;
      const URL = `https://www.eia.gov/realtime_grid/sixMonthFiles/${filename}`;
      const response = await fetch(URL).catch(() => {
        console.errror(`There was an error fetching ${URL}`);
      });

      const data = await response.text();
      const file = fs.createWriteStream(`${outputFilePath}/${filename}`);

      file.write(data);
      file.end();
      resolve();
    })();
  });
};
