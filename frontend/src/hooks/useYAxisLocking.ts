import { chart, ChartOptions } from "highcharts";
import * as React from "react";
import { Series } from "../components/figures";

// type UseYAxisLockingOpts = {
//   isStackedByAxis: boolean[];
// }

const getArrayMax = (array: Array<number | null>): number => {
  let max = 0;
  array.forEach(value => {
    if (value && value > max) {
      max = value;
    }
  })
  return max;
}

const getArrayMin = (array: Array<number | null>): number => {
  let min = Infinity;
  array.forEach(value => {
    if (value && value < min) {
      min = value;
    }
  })
  return min;
}

const areSeriesStacked = (arrayOfSeriesArrays: Series[]) => {
  return arrayOfSeriesArrays.some(series => {return series.type === 'area' || series.type === 'column' || !!series.stacking});
}

const getAggOfSeriesArray = (seriesArray: Series[], aggregationFunc: (array: Array<number | null>) => number): number | undefined => {
  if (seriesArray.length > 0) {
    if (areSeriesStacked(seriesArray)) {
      // debugger
      let yAggOfOverlaidSeries = 0; // for calculating ymax of overlaid series, which we need to use as our overall yMax if it happens to be greater than the yMax of the stacked series
      // if some series are specified as stacking, that means there might be series that shouldn's stack, but are overlaid instead - if so, filter those out so they don't contribute to yMax. otherwise, if none are specified as stacking, assume they are all stacked.
      if (seriesArray.some(series => !!series.stacking)) {
        // find aggregate value of overlaid series (if any)
        const overlaidSeriesOnThisYAxis = seriesArray.filter(series => !series.stacking);
        yAggOfOverlaidSeries = aggregationFunc(overlaidSeriesOnThisYAxis.map(series => aggregationFunc(series.data))) || 0;
        // console.log(yMaxOfOverlaidSeries)
        seriesArray = seriesArray.filter(series => !!series.stacking); // remove series that don't stack, but are just overlaid
      }
      // find aggregate value of stacked series
      const yAggOfStackedSeries = aggregationFunc(new Array(seriesArray[0].data.length).fill(null).map((o, index) => {
        const arrayOfYValuesAtX = seriesArray.map(serie => serie.data[index] || 0)?.flat();
        const sumOfYValuesAtX = arrayOfYValuesAtX.reduce((a, b) => a + b);
        return sumOfYValuesAtX;
      }));
      return aggregationFunc([yAggOfStackedSeries || 0, yAggOfOverlaidSeries]);
    } else {
      return aggregationFunc(seriesArray.map(series => aggregationFunc(series.data)));
    }
  } else {
    return undefined;
  }
}

export const getMaxOfSeriesArray = (seriesArray: Series[]): number | undefined => {
  return getAggOfSeriesArray(seriesArray, getArrayMax);
}

export const getMinOfSeriesArray = (seriesArray: Series[]): number | undefined => {
  return getAggOfSeriesArray(seriesArray, getArrayMin);
}

export const useYAxisLocking = (
  isYAxisLocked: boolean,
  arrayOfChartOptions: Array<ChartOptionsWithSeries | null> | undefined,
  // opts?: UseYAxisLockingOpts
): Array<number | null> => {
  const [biggestYMaxes, setBiggestYMaxes] = React.useState([null as number | null]);

  React.useEffect(() => {
    if (isYAxisLocked) {
      const yMaxPairsByDataset = arrayOfChartOptions?.map(chartOptions => {
        if (!chartOptions) {
          return undefined;
        }
        return chartOptions.yAxis?.map((yAxis, yAxisIndex) => {
          if (yAxis.max) { // if Y max has already been calculated somewhere, just use that
            return yAxis.max
          } else { // calculate from series data
            let seriesOnThisYAxis = chartOptions.series.filter(serie => serie.yAxis === yAxisIndex);
            return getMaxOfSeriesArray(seriesOnThisYAxis)
          }
        })
      });
      const possibleYAxes = [0,1];
      const biggestYMaxesHere = possibleYAxes.map(yAxis => {
        return getArrayMax(yMaxPairsByDataset?.map(pair => pair ? (pair[yAxis] || 0) : null) || []) || null;
      })
      setBiggestYMaxes(biggestYMaxesHere);
    }
  }, [isYAxisLocked, JSON.stringify(arrayOfChartOptions)])

  if (isYAxisLocked) {
    return biggestYMaxes;
  } else {
    return [null, null];
  }
}