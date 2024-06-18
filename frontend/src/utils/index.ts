// response format
// {
//   columns: ["value", "stage", "pathway"],
//   data: [
//     [0.0, "Enduse", "My Pathway"],
//     [47.792, "GateToEnduse", "My Pathway"],
//     [538.7538, "Process", "My Pathway"],
//     [27.7194, "Midstream", "My Pathway"],
//     [0.0, "Upstream", "My Pathway"],
//   ],
//   title: "Life Cycle CO2 Emissions",
//   unit: "kg",
//   value: "CO2",
// };

// transform response.data tuples into objects with column
// keys from response.columns
const addColumnKeys = (
  response: PathwayAnalysisResponseWithUnformattedData,
  groupBy: string[] = []
) => {
  return response.data.reduce((acc: Data[], curr): Data[] => {
    const item: {
      [key: string]: string | number;
    } = {};
    response.columns.forEach((columnName, index) => {
      item[columnName] = curr[index];
    });

    const finder = (data: Data) => {
      if (groupBy?.length === 0) {
        return false;
      } else {
        let ret = true;
        groupBy?.forEach((name) => {
          ret = ret && data[name] === item[name];
        });
        return ret;
      }
    };

    const existing = acc.find(finder);

    // combine more granular sub-stages in response
    if (
      existing &&
      typeof existing.value === "number" &&
      typeof item.value === "number"
    ) {
      const removeExisting = acc.filter((p) => !finder(p));
      return [
        ...removeExisting,
        { ...existing, value: existing.value + item.value },
      ];
    }
    return [...acc, item];
  }, []);
};

export const groupByKeys = (
  response: PathwayAnalysisResponseWithUnformattedData,
  keys?: string[]
): PathwayAnalysisResponse & {
  data: Data[];
} => {
  const data = addColumnKeys(response, keys);
  return { ...response, data };
};

// group by pathway, e.g.
// [
//   { "pathway": "A", "Enduse": 111.0, "Process": 222.0 },
//   { "pathway": "B", "Enduse": 333.0, "Process": 444.0 },
// ]
export const groupByPathway = (
  response: PathwayAnalysisResponseWithUnformattedData
): PathwayAnalysisResponse & {
  data: Data[];
} => {
  const series = response.columns.find(
    (name) => name !== "value" && name !== "pathway"
  );
  if (!series) {
    throw "no series found in analysis response";
  }

  const grouped = groupByKeys(response, ["pathway", "stage"]);

  const data = grouped.data.reduce((acc: Data[], curr) => {
    const val =
      typeof curr.value === "number"
        ? parseFloat(curr.value.toFixed(2))
        : curr.value;
    const existingItem = acc.find(
      (item: Data) => item.pathway === curr.pathway
    );
    if (typeof existingItem === "object") {
      return [
        ...acc.filter((item: Data) => item.pathway !== curr.pathway),
        { ...existingItem, [curr[series]]: val },
      ];
    } else {
      return [...acc, { pathway: curr.pathway, [curr[series]]: val }];
    }
  }, []);

  return { ...grouped, data };
};

export function dateStringtoUTC(dateStr: string, hour?: string): number {
  const [month, day, year] = dateStr.split("/");

  if (year.length !== 2 && year.length !== 4) {
    throw new Error(`The year ${year} must be either two or four digits`);
  }
  // if we only have two digits for the year, we assume we're in the 2000s
  const yearInt = parseInt(year.length === 4 ? year : `20${year}`, 10);
  const monthInt = parseInt(month, 10) - 1;
  const dayInt = parseInt(day, 10);
  const hourInt = parseInt(hour || "0", 10);

  if (typeof hour !== "undefined") {
    return Date.UTC(yearInt, monthInt, dayInt, hourInt);
  }

  return Date.UTC(yearInt, monthInt, dayInt);
}

export const getChangeInDemandLast7Days = (
  set1: number[][],
  set2: number[][],
  lastN: number
): string => {
  let total1 = 0;
  let total2 = 0;

  set1.slice(lastN).forEach(([, value]) => {
    total1 += value;
  });

  set2.slice(lastN).forEach(([, value]) => {
    total2 += value;
  });
  return (((total1 - total2) / total1) * 100).toFixed(2);
};

export const capitalStr = (phrase: string): string =>
  phrase.charAt(0).toUpperCase() + phrase.slice(1);

export const capitalSentence = (sentence: string): string =>
  sentence.split(" ").map(capitalStr).join(" ");

export const formatUserInput = (val: string | number): string | number => {
  let formattedVal = val;
  if (typeof val === "string") {
    if (!Number.isNaN(parseFloat(val))) {
      formattedVal = parseFloat(val);
    } else if (!Number.isNaN(parseInt(val))) {
      formattedVal = parseInt(val);
    }
  }
  return formattedVal;
};

export const roundToHundredth = (value: number): number =>
  Math.ceil(value * 100) / 100;

export const isBrowser = (): boolean => typeof window !== "undefined";

export const groupUserInputs = (
  userInputs: UserInputProperties[],
  dividingInputs: Record<string, string>
) => {
  const inputGroups: InputGroup[] = [];

  let currentInputGroup: InputGroup = {
    title: undefined,
    userInputs: [],
  };

  for (const userInput of userInputs) {
    if (userInput.name in dividingInputs) {
      // start of new group
      inputGroups.push(currentInputGroup);

      currentInputGroup = {
        title: dividingInputs[userInput.name],
        userInputs: [],
      };
    }

    currentInputGroup.userInputs.push(userInput);
  }
  inputGroups.push(currentInputGroup);

  return inputGroups;
};

export const triggerResize = () => {
  // console.log('triggerResize');
  window.setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  }, 1)
}

export const throttle = (func: Function, delay: number) => {
  let inProgress = false;
  return (...args) => {
    if (inProgress) {
      console.log('throttled func in progress; skipping')
      return;
    }
    inProgress = true;
    setTimeout(() => {
      func(...args); // Consider moving this line before the set timeout if you want the very first one to be immediate
      inProgress = false;
    }, delay);
  }
}

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
export const debounce = (func, wait, immediate) => {
  var timeout;
  return function() {
    var context = this, args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

export const colors = {
  blue: "#5B9BD5",
  green: "#62993E",
  yellow: "#FFC000",
  orange: "#ED7D31",
  gray: "#929292",
  black: "#000000",
  red: "red",
};

export const capitalize = (string: string): string => {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export const formatLabelString = (string: string): string => {
  return string.replace(/([A-Z]+)/g, ' $1').trim()
}

export const getHeaderTitle = (path?: string) => {
  // console.log(path)
  if (!path) {
    path = location.pathname.split('#')[0].split('?')[0];
  }
  if (path.includes(`404`)) {
    return "404: Not Found";
  } else if (path.includes(`covid`)) {
    return "COVID-19 Analysis";
  } else if (path.includes('dashboard')) {
    return 'Dashboard';
  }
  //else if (path.includes(`app/cars`)) {
    // return "Cars";
  // } else if (path.includes(`app/power`)) {
  //   return "Power";
  // } else if (path.includes(`app/power-historic`)) {
  //   return "Power Historic";
  // } else if (path.includes(`app/power-greenfield`)) {
  //   return "Power Greenfield";
  // } else if (path === `app/pathways`) {
  //   return "Pathways";
  // } else if (path === "/app" || path === "/app/") {
  //   return "Create Emissions (LCA) Pathway";
  // } else if (path.includes(`/app/emissions`)) {
  //   return "Emissions (LCA)";
  // } else if (path.includes(`/app/costs`)) {
  //   return "Costs (TEA)";
  // }
  else {
    return "";
  }
};

// concat only array-like arrays, ignoring things that are not actually arrays
export const concatOnlyActualArrays = (...arrays) => {
  return [].concat(...arrays.filter(Array.isArray));
}

export const sumArray = (array: number[]) => {
  return array.reduce((acc, o) => acc + (o ?? 0), 0)
}
  
export const generateUniqueIntId = () => {
  return parseInt(new Array(10).fill().map(i => Math.floor(Math.random() * 10)).reduce((acc,o) => acc + o.toString()))
}

export const flattenDeep = (items: any[] | undefined) => {
  const flat = [] as unknown[];

  if (Array.isArray(items)) {
    items.forEach(item => {
      if (Array.isArray(item)) {
        flat.push(...flattenDeep(item));
      } else {
        flat.push(item);
      }
    });

  }

  return flat;
}

export const unique = (array: any[] | undefined) => {
  if (Array.isArray(array)) {
    return [...new Set(array)]
  }
}

export const formatDecimal = (val: number) => {
  if (val === 0) {
    return '0';
  } else if (Math.abs(val) > 10) {
    return val.toFixed(0);
  } else if (Math.abs(val) > 1) {
    return val.toFixed(1);
  } else {
    return val.toFixed(2);
  }
};

export const groupBy = function(data: Array<any>, key: string) { // `data` is an array of objects, `key` is the key (or property accessor) to group by
  // reduce runs this anonymous function on each element of `data` (the `item` parameter,
  // returning the `storage` parameter at the end
  return data.reduce(function(storage, item) {
    // get the first instance of the key by which we're grouping
    var group = item[key];
    
    // set `storage` for this instance of group to the outer scope (if not empty) or initialize it
    storage[group] = storage[group] || [];
    
    // add this item to its group within `storage`
    storage[group].push(item);
    
    // return the updated storage to the reduce function, which will then loop through the next 
    return storage; 
  }, {}); // {} is the initial value of the storage
};

export const kebabCase = (string: string | undefined) => {
  return string?.replace(/ /gi, '-').toLowerCase();
}