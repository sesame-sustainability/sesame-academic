// When we're comparing + averaging years,
// the data sets must all begin on the first Wednesday of the year
// which aligns with 1/1/2020 which is a Wednesday.
// As such, we ignore all dates before the first Wed of the year
exports.datesToIgnore = [
  "01/01/2016",
  "01/02/2016",
  "01/03/2016",
  "01/04/2016",
  "01/05/2016",
  "01/01/2017",
  "01/02/2017",
  "01/03/2017",
  "01/01/2018",
  "01/02/2018",
  "01/01/2019",
  "01/01/2021",
  "01/02/2021",
  "01/03/2021",
  "01/04/2021",
  "01/05/2021",
];

// Monday of 12th week
exports.firstDates = {
  2016: "03/14/2016",
  2017: "03/20/2017",
  2018: "03/19/2018",
  2019: "03/18/2019",
  2020: "03/16/2020",
  2021: "03/15/2021",
};

const currentYear = new Date().getFullYear();
const range = (start, stop, step) =>
  Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);

// generates range from 2016 to current year
exports.analysisYears = range(2016, currentYear, 1).map((year) => `${year}`);

exports.balancingAuthorities = [
  "CISO",
  "FPL",
  "MISO",
  "NYIS",
  "SWPP",
  "ERCO",
  // "PJM",
  // "ISNE",
];
