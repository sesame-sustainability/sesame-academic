import * as React from "react"
// import { throttle } from "../utils";
import useResizeObserver from '@react-hook/resize-observer'
import { throttle } from "lodash";
import usePrevious from "./usePreviousValue";
import { CHART_ANIMATION_DURATION, CHART_ASPECT_RATIO } from "../utils/constants";
import { debounce } from "../utils";

export const useWidth = (target) => {
  const [width, setWidth] = React.useState()

  React.useLayoutEffect(() => {
    setWidth(target.current?.getBoundingClientRect().width)
  }, [target])

  // Where the magic happens
  useResizeObserver(target, (entry) => setWidth(entry.contentRect.width))
  return width;
}

export const resizeChartToWidth = ({
  chart,
  width,
  height,
  animation = false,
  // animation = {duration: CHART_ANIMATION_DURATION},
}: {
  chart: unknown;
  width: number | undefined;
  height?: number;
  animation?: boolean | object;
}) => {
  // console.log(height);
  if (chart && width) {
    var legendSpace = chart.legend.allItems.length > 0 ? (chart.legend.legendHeight - chart.legend.padding) : 0;
    if (height) {
      console.log(height, legendSpace);
    }
    const newChartHeight = height ? height + legendSpace : Math.round(width * CHART_ASPECT_RATIO + legendSpace);
    // chart.setSize(width, newChartHeight, animation)//, false)//{duration: 100}); // last prop enables/disables animation when resizing
  }
}

const useThrottle = (cb, delay) => {
  const options = { leading: false, trailing: true }; // add custom lodash options
  const cbRef = React.useRef(cb);
  // use mutable ref to make useCallback/throttle not depend on `cb` dep
  React.useEffect(() => { cbRef.current = cb; });
  return React.useCallback(
    // throttle((...args) => cbRef.current(...args), delay, options),
    debounce((...args: Array<any>) => cbRef.current(...args), delay, false),
    // throttle((...args) => cbRef.current(...args), delay),//, options),
    [delay]
  );
}

export const useChartResizing = ({
  chartRef,
  containerRef,
  deps,
  height,
}: {
  chartRef: React.MutableRefObject<React.ReactElement | null>,
  containerRef: React.MutableRefObject<HTMLDivElement | null>,
  deps?: React.DependencyList,
  height?: number,
}) => {

  // console.log('useChartResizing');

  const width = useWidth(containerRef);
  const previousWidth = usePrevious(width);
  const wasWidthResized = previousWidth && width !== previousWidth;

  const legendHeight = chartRef.current?.chart?.legend.legendHeight;
  const previousLegendHeight = usePrevious(legendHeight);
  const wasLegendResized = legendHeight && legendHeight !== previousLegendHeight;

  const handleResize = () => {
    const chart = chartRef.current?.chart;
    if (!chart) {
      return null;
    }
    // if (!chart.justLoaded && (wasWidthResized || wasLegendResized)) { // don't resize on first chart load
      // console.log(width, previousWidth);
      resizeChartToWidth({
        chart,
        width,
        height,
      });
    // } else {
      // chart.justLoaded = false;
    // }
  }

  const throttledCb = useThrottle(handleResize, 100);
  // usage with useEffect: invoke throttledCb on value change
  React.useEffect(throttledCb, deps ? deps.concat(width) : [width]);

}




