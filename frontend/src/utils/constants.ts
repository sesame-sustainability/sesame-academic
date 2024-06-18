const dateTimeLabelFormats = {
  millisecond: "%H:%M:%S.%L",
  second: "%H:%M:%S",
  minute: "%H:%M",
  hour: "%H:%M",
  day: "%A",
  week: "%b %e",
  month: "%B",
  year: "%Y",
};

const fontSize = 13 // make sure this is the same as what's in layout.css for html font size

const bodyFontFamily = [
  `system-ui`,
  `-apple-system`,
  `BlinkMacSystemFont`,
  `Segoe UI`,
  `Roboto`,
  `Ubuntu`,
  `Helvetica Neue`,
  `sans-serif`,
];

const analysisYears: AnalysisYearsTuple = [
  "2016",
  "2017",
  "2018",
  "2019",
  "2020",
  "2021",
];

const balancingAreas: BalancingAreaTuple = [
  "CISO",
  "ERCO",
  "SWPP",
  "MISO",
  "NYIS",
  "FPL",
  // "ISNE",
  // "PJM",
];

const balancingAreasDisplay = {
  CISO: { short: "CAISO", long: "California" },
  ERCO: { short: "ERCOT", long: "Texas" },
  SWPP: { short: "SWPP", long: "Southwest" },
  MISO: { short: "MISO", long: "Midwest and South" },
  NYIS: { short: "NYISO", long: "New York" },
  FPL: { short: "FPL", long: "Florida" },
  ISNE: { short: "ISO-NE", long: "" },
  PJM: { short: "PJM", long: "" },
};

const colors: { [key: string]: { [key: string]: string } } = {
  teal: {
    "100": "#e6fffa",
    "200": "#b2f5ea",
    "300": "#81e6d9",
    "400": "#4fd1c5",
    "500": "#38b2ac",
    "600": "#319795",
    "700": "#2c7a7b",
    "800": "#285e61",
    "900": "#234e52",
  },
  blue: {
    "100": "#ebf8ff",
    "200": "#bee3f8",
    "300": "#90cdf4",
    "400": "#63b3ed",
    "500": "#4299e1",
    "600": "#3182ce",
    "700": "#2b6cb0",
    "800": "#2c5282",
    "900": "#2a4365",
  },
  indigo: {
    "100": "#ebf4ff",
    "200": "#c3dafe",
    "300": "#a3bffa",
    "400": "#7f9cf5",
    "500": "#667eea",
    "600": "#5a67d8",
    "700": "#4c51bf",
    "800": "#434190",
    "900": "#3c366b",
  },
  purple: {
    "100": "#faf5ff",
    "200": "#e9d8fd",
    "300": "#d6bcfa",
    "400": "#b794f4",
    "500": "#9f7aea",
    "600": "#805ad5",
    "700": "#6b46c1",
    "800": "#553c9a",
    "900": "#44337a",
  },
  pink: {
    "100": "#fff5f7",
    "200": "#fed7e2",
    "300": "#fbb6ce",
    "400": "#f687b3",
    "500": "#ed64a6",
    "600": "#d53f8c",
    "700": "#b83280",
    "800": "#97266d",
    "900": "#702459",
  },
  red: {
    "100": "#fff5f5",
    "200": "#fed7d7",
    "300": "#feb2b2",
    "400": "#fc8181",
    "500": "#f56565",
    "600": "#e53e3e",
    "700": "#c53030",
    "800": "#9b2c2c",
    "900": "#742a2a",
  },
  orange: {
    "100": "#fffaf0",
    "200": "#feebc8",
    "300": "#fbd38d",
    "400": "#f6ad55",
    "500": "#ed8936",
    "600": "#dd6b20",
    "700": "#c05621",
    "800": "#9c4221",
    "900": "#7b341e",
  },
  yellow: {
    "100": "#fffff0",
    "200": "#fefcbf",
    "300": "#faf089",
    "400": "#f6e05e",
    "500": "#ecc94b",
    "600": "#d69e2e",
    "700": "#b7791f",
    "800": "#975a16",
    "900": "#744210",
  },
  green: {
    "100": "#f0fff4",
    "200": "#c6f6d5",
    "300": "#9ae6b4",
    "400": "#68d391",
    "500": "#48bb78",
    "600": "#38a169",
    "700": "#2f855a",
    "800": "#276749",
    "900": "#22543d",
  },
  gray: {
    "100": "#f7fafc",
    "200": "#edf2f7",
    "300": "#e2e8f0",
    "400": "#cbd5e0",
    "500": "#a0aec0",
    "600": "#718096",
    "700": "#4a5568",
    "800": "#2d3748",
    "900": "#1a202c",
  },
};

const transparent = "transparent";
const current = "currentColor";
const black = "#000";
const white = "#fff";

// responsive graph rules
const responsive = {
  rules: [
    {
      condition: {
        maxWidth: 500,
      },
      chartOptions: {
        title: {
          y: 80,
          margin: 90,
        },
        yAxis: {
          labels: {
            align: "left",
            x: 0,
            y: -2,
          },
        },
      },
    },
  ],
};

const maxComparisonResultCols = 3;

const CHART_ASPECT_RATIO = 0.5;

const CHART_ANIMATION_DURATION = 400;

export {
  fontSize,
  colors,
  black,
  white,
  transparent,
  current,
  analysisYears,
  bodyFontFamily,
  balancingAreas,
  balancingAreasDisplay,
  dateTimeLabelFormats,
  responsive,
  maxComparisonResultCols,
  CHART_ASPECT_RATIO,
  CHART_ANIMATION_DURATION,
};

