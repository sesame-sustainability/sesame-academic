import React, { useEffect, useState } from "react";
import Highcharts, { ChartOptions } from "highcharts";
import HighchartsReact from "highcharts-react-official";
import merge from "deepmerge";
import { bodyFontFamily, CHART_ANIMATION_DURATION, CHART_ASPECT_RATIO, maxComparisonResultCols } from "../utils/constants";
import { Select } from "./styles"
import { TiledColumn } from "./tiledColumn";
import { ComparisonRow, ModuleStateContext } from "./comparableResultsModule";
import { ChartExportButton } from "./chartExportButton";
import * as Styles from "./styles"
import { useYAxisLocking } from "../hooks/useYAxisLocking";
import { useMemoCompare } from "../hooks/useMemoCompare";
import { resizeChartToWidth, useChartResizing } from "../hooks/useChartResizing";
import { Toggle } from "./toggle";
import Accordion from "./accordion";
import { colors } from "../utils/constants";

export const chartColors = {
  blue: "#5B9BD5",
  green: "#70ac46",//"#62993E",
  yellow: "#FFC000",
  orange: "#ED7D31",
  gray: "#929292",
  black: "#000000",
  red: "red",
  indigo_light: colors.indigo['300'],
  indigo_dark: colors.indigo['700'],
  teal_light: colors.teal['300'],
  teal_dark: colors.teal['700'],
};

export const maxBarWidth = 20;

const legendHeightGuess = 50;

export type Series = {
  name: string;
  yAxis: number;
  type: string;
  data: Array<number | null>;
  color?: string;
  stacking?: string;
};

export type Dataset = {
  label: string;
  id?: string;
  data: number[][];
  columns: string[];
  axis?: number;
  unit?: string;
  scalar?: number;
  scalarUnit?: string;
  type?: string;
  color?: string;
  style?: string;
  seriesStyles?: Record<string, string>;
};

export type FigureInput = {
  name: string;
  label: string;
  options: string[];
};

export type FigureType = {
  inputs: FigureInput[];
  title: string;
  categories: (string | number)[];
  series: (inputStates: Record<string, string>, index: number) => Series[]; // generate series data form input states
  chartOptions?: Record<string, unknown>;
};

export type FigureSetType = {
  inputs: FigureInput[]; // inputs shared by all figures
  figures: FigureType[];
};

type StickyFigureControlsProps = {
  nonComparisonModeTop?: string,
  comparisonModeTop?: string,
}

export const StickyFigureControls: React.FC<StickyFigureControlsProps> = ({
  children,
  nonComparisonModeTop = '',
  comparisonModeTop = '',
}) => {
  const { chartControlAllocation, isComparisonMode } = React.useContext(ModuleStateContext);
  const style = {top: isComparisonMode ? comparisonModeTop : nonComparisonModeTop};
  return (
    <ComparisonRow
      className={`sticky z-[9] bg-gray-50 border-b border-gray-300 shadow-sm ${isComparisonMode ? '' : 'py-2 non-comparison-cell'}`}
      style={style}
      content={children}
    />
  )
}

// type ResizingChartContainerProps = {
//   chartProps?: any,
//   // stuff?: any,
// }

// export const ResizingChartContainer: React.FC<ResizingChartContainerProps> = ({chartProps, children}) => {
//   const chartRef = React.useRef(); // can pass in a ref if we already have one, else make a new one
//   const containerRef = React.useRef();
//   console.log(chartProps);
//   useChartResizing(chartRef, containerRef);
//   return (
//     <div ref={containerRef}>
//       <HighchartsReact {...chartProps} ref={chartRef} />
//     </div>
//   )
// }

export const FigureInputs = React.memo(
  ({
    inputs,
    inputStates,
    setInputStates,
    layout = 'column',
  }: {
    inputs: FigureInput[];
    inputStates: Record<string, string>;
    setInputStates: React.Dispatch<
      React.SetStateAction<Record<string, string>>
    >;
    layout: 'row' | 'column';
  }) => {

    const { comparisonCases } = React.useContext(ModuleStateContext)

    // const renderCount = React.useRef(0)

    const setInputState = (name: string) => {
      return (value: string) => {
        setInputStates({ ...inputStates, [name]: value });
      };
    };

    useEffect(() => {
      // default to first option
      const defaults = inputs.reduce(
        (acc: Record<string, string>, input: FigureInput) => {
          if (inputStates[input.name] === undefined) {
            acc[input.name] = input.options[0];
          }
          return acc;
        },
        {}
      );

      setInputStates((prevInputState) => {
        return { ...prevInputState, ...defaults };
      });
    }, [inputs, setInputStates]);

    const Dropdown = ({
      options,
      selected,
      onChange,
    }: {
      options: string[];
      selected: string;
      onChange: (option: string) => void;
    }) => {
      return (
        <Select
          value={selected}
          onChange={(e) => {
            e.preventDefault();
            onChange(e.target.value);
          }}
          className="flex-1 min-w-[6rem]"
        >
          {options.map((option, i) => {
            return (
              <option key={i} value={option}>
                {option}
              </option>
            );
          })}
        </Select>
      );
    };

    return (
      <div
        className={`figure-controls flex ${layout === 'column' ? 'flex-col w-80' : 'flex-row'} max-w-full h-full !py-0`}
      >
        {/* <div className="py-1 px-2 bg-red-500 text-white">FigureInputs rendered {(renderCount.current ++)} time(s)</div> */}
        {inputs.map((input, index) => {
          return (
            <div key={input.name} className={`flex flex-row items-center ${layout === 'column' ? 'flex-wrap mb-2' : (index < inputs.length - 1 ? 'mr-4' : '')}`}>
              {input.label &&
                <Styles.Label className={`${layout === 'column' ? 'w-1/5 min-w-[4rem] mb-1' : ''} mr-3 flex-initial`}>{input.label}</Styles.Label>
              }
              <Dropdown
                options={input.options}
                selected={inputStates[input.name]}
                onChange={setInputState(input.name)}
              />
            </div>
          );
        })}
      </div>
    );
  }
);
FigureInputs.displayName = "FigureInputs";

export const valueFormatter = ({
  value,
  max = null,
}: {
  value: number;
  max?: null | number;
}): string => {
  // max represents the max value possible on the y-axis
  let decimals = 0;
  if (max === null) {
    max = value;
  }
  if (1 < max && max <= 10) {
    decimals = 1;
  } else if (0 < max && max <= 1) {
    decimals = 2;
  }
  if (value === null) {
    return '0';
  }
  return value.toFixed(decimals);
};

export const defaultChartOptions = (categories: (string | number)[], years: boolean = true) => {
  let plotLines: unknown[] = [];

  if (years) {
    const initialYear = categories[0] as number;

    plotLines = [
      {
        value: 2019 - initialYear,
        label: {
          text: "Future",
          style: {
            color: "black",
            transform: "translate(6px, 10px)",
            fontWeight: "bold",
          },
        },
        zIndex: 10,
      },
      {
        value: 2019 - initialYear,
        label: {
          text: "Past",
          style: {
            transform: "translate(-41px, 10px)",
            color: "black",
            fontWeight: "bold",
          },
        },
        zIndex: 10,
      },
    ];
  }

  return {
    exporting: {
      enabled: true,
      fallbackToExportServer: false
    },
    chart: {
      type: "area",
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
      height: '65%',//100 * CHART_ASPECT_RATIO + '%',
      spacingBottom: 70,
      spacingTop: 10,
      spacingLeft: 5,
      spacingRight: 10,
      // marginRight: 20,
      // reflow: false,
      animation: {duration: CHART_ANIMATION_DURATION},
      // events: {
      //   load() {
      //     const chart = this;
      //     // chart.chartHeight = 200;
      //     // setTimeout(() => {
      //     //   resizeChartToWidth({chart, width: chart.containerWidth});
      //     // }, 1)
      //     // const legendHeight = chart.legend.legendHeight;
      //     // const chartWidth = chart.chartWidth;
      //     // chart.setSize(chartWidth * CHART_ASPECT_RATIO + legendHeight);
      //     this.justLoaded = true; // this custom flag is used by useChartResizing to avoid resizing charts on initial load
      //   },
      // }
    },
    legend: {
      // useHTML: true,
      align: 'center',
      verticalAlign: 'bottom',
      layout: 'horizontal',
      itemDistance: 10,
      itemMarginTop: 1,
      itemMarginBottom: 10,
      symbolPadding: 3,
      floating: true,
      maxHeight: 70,
      y: 70,
      itemStyle: {
        color: '#666',
        fontWeight: 'normal'
      }
    },
    // legend: {
    //   layout: "vertical",
    //   align: "left",
    //   verticalAlign: "middle",
    //   itemMarginTop: 1,
    //   itemMarginBottom: 3,
    //   itemStyle: {
    //     color: '#666',
    //     fontWeight: 'normal'
    //   }
    // },
    navigation: {
      buttonOptions: {
        enabled: false // we're using a custom export button
      }
    },
    credits: {
      enabled: false,
    },
    xAxis: {
      categories,
      tickPlacemark: "on",
      title: {
        enabled: false,
      },
      labels: {
        step: 10,
      },
      plotLines,
    },
    yAxis: [
      {
        title: {
          enabled: false,
        },
        labels: {
          // these keys required to satisfy TS
          axis: {
            max: 0,
          },
          value: 0,
          formatter(): unknown {
            return valueFormatter({ max: this.axis.max, value: this.value });
          },
        },
        max: undefined as undefined | number,
        tickAmount: undefined as undefined | number,
      },
      {
        title: {
          enabled: false,
        },
        labels: {
          style: {
            color: "#FF0000",
          },
        },
        opposite: true,
        type: "line",
        min: 0,
      },
    ],
    title: {
      text: null,
    },
    plotOptions: {
      series: {
        animation: {duration: CHART_ANIMATION_DURATION},
      },
      area: {
        stacking: "normal",
        animation: {duration: CHART_ANIMATION_DURATION},
        lineWidth: 1,
        // boostThreshold: 2000,
        marker: {
          enabled: false,
        },
      },
      line: {
        animation: {duration: CHART_ANIMATION_DURATION},
        marker: {
          enabled: false,
        },
        lineWidth: 2,
        // boostThreshold: 2000,
      },
      column: {
        animation: {duration: CHART_ANIMATION_DURATION},
        stacking: "normal",
        marker: {
          enabled: false,
        },
      },
    },
    responsive: {
      rules: [
        {
          condition: {
            maxWidth: 250,
          },
          chartOptions: {
            chart: {
              height: '80%',
            },
          },
        },
        {
          condition: {
            maxWidth: 350,
          },
          chartOptions: {
            chart: {
              height: '75%',
            },
          },
        },
        {
          condition: {
            minWidth: 700,
          },
          chartOptions: {
            chart: {
              height: '40%',
              spacingBottom: 10,
            },
            legend: {
              align: 'left',
              verticalAlign: 'middle',
              floating: false,
              y: null,
              layout: 'vertical',
              maxHeight: undefined,
            },
          }
        }
      ]
    },
    // responsive: {
    //   rules: [
    //     {
    //       condition: {
    //         maxWidth: 300
    //       },
    //       chartOptions: {
    //         // chart: {
    //         //   height: '90%',
    //         //   // spacingBottom: 60,
    //         // },
    //         legend: {
    //           align: 'center',
    //           verticalAlign: 'bottom',
    //           layout: 'horizontal',
    //           itemDistance: 10,
    //           itemMarginBottom: 10,
    //           symbolPadding: 3,
    //           // floating: true,
    //           // maxHeight: 60,
    //           // y: 70,
    //         }
    //       }
    //     },
    //     {
    //       condition: {
    //         maxWidth: 500
    //       },
    //       chartOptions: {
    //         // chart: {
    //         //   height: '70%',
    //         //   // spacingBottom: 60,
    //         // },
    //         legend: {
    //           align: 'center',
    //           verticalAlign: 'bottom',
    //           layout: 'horizontal',
    //           itemDistance: 10,
    //           itemMarginBottom: 10,
    //           symbolPadding: 3,
    //           // floating: true,
    //           // maxHeight: 60,
    //           // y: 70,
    //         }
    //       }
    //     },
    //   ]
    // },
    tooltip: {
      // following keys satisfy TS compiler re: accessing on `this`
      x: "",
      y: 0,
      series: {
        name: "",
        yAxis: {
          max: 0,
        },
      },
      point: {
        stackTotal: 0,
      },
      borderWidth: 0,
      formatter(): unknown {
        const max = this.series.yAxis.max;
        const value = this.y;
        let ret = `<b>${this.x}</b><br />${
          this.series.name
        }: </b><b>${valueFormatter({ value })}`;
        if (this.point.stackTotal) {
          ret += `</b><br />Total: <b>${valueFormatter({
            value: this.point.stackTotal,
          })}</b>`;
        }
        return ret;
      },
    },
  };
};

// export const useContainerDimensions = myRef => {
//   const getDimensions = () => ({
//     width: myRef.current.offsetWidth,
//     height: myRef.current.offsetHeight
//   })

//   const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

//   useEffect(() => {
//     const handleResize = () => {
//       setDimensions(getDimensions())
//     }

//     if (myRef.current) {
//       setDimensions(getDimensions())
//     }

//     window.addEventListener("resize", handleResize)

//     return () => {
//       window.removeEventListener("resize", handleResize)
//     }
//   }, [myRef])

//   return dimensions;
// };

export const isNextChartEqualToPrev = (prevProps, nextProps) => {
  const areEqual = (
    JSON.stringify(prevProps.comparisonCaseId) === JSON.stringify(nextProps.comparisonCaseId)
    &&
    JSON.stringify(prevProps.yAxesMaxes) === JSON.stringify(nextProps.yAxesMaxes)
    &&
    JSON.stringify(prevProps.chartOptions?.series) === JSON.stringify(nextProps.chartOptions?.series)
    &&
    JSON.stringify(prevProps.chartOptions?.yAxis) === JSON.stringify(nextProps.chartOptions?.yAxis)
    // &&
    // JSON.stringify(prevProps.chartOptions?.series.map(serie => serie.name)) === JSON.stringify(nextProps.chartOptions?.series.map(serie => serie.name))
  );
  // console.log(prevProps.chartOptions);
  // if (nextProps.comparisonIndex === 0) {
  //   console.log('=========')
    // console.log('are charts equal?', areEqual);
  //   console.log('=========')
  // }
  // return false
  return areEqual;
}

const Chart = React.memo(({
  chartOptions,
  figure,
  inputStateHandler,
  index,
  yAxesMaxes,
  comparisonCaseId,
}: {
  chartOptions: ChartOptions | null;
  figure: FigureType;
  inputStateHandler: InputStateHandler;
  index: number;
  yAxesMaxes?: Array<number | null>;
  comparisonCaseId: number;
}) => {
  const chartRef = React.useRef(null);
  const containerRef = React.useRef(null);
  // useChartResizing({
  //   chartRef,
  //   containerRef,
  //   deps: [JSON.stringify(chartOptions), JSON.stringify(inputStateHandler.inputStates)]
  // });
  const { isComparisonMode, chartControlAllocation } = React.useContext(ModuleStateContext);

  // const isLoading = comparisonCases?.[index]?.isLoading;

  React.useEffect(() => {
    chartRef.current?.chart?.yAxis?.[0]?.setExtremes(null, yAxesMaxes?.[0] || null);
    chartRef.current?.chart?.yAxis?.[1]?.setExtremes(null, yAxesMaxes?.[1] || null);
  }, [yAxesMaxes]);

  // console.log(chartOptions)

  return (
    <div className={isComparisonMode ? "border-l border-gray-300 py-2" : ''}>
      {/* <div className="py-1 px-2 bg-red-500 text-white">Chart rendered {(renderCount.current ++)} time(s)</div> */}
      {/* {isLoading ? */}
        {/* <Styles.Loader /> */}
        {/* : */}
        <div className="relative">
          {chartOptions &&
            <>
              {!isComparisonMode &&
                <FigureInputs
                  inputs={figure.inputs}
                  inputStates={inputStateHandler.inputStates}
                  setInputStates={inputStateHandler.setInputStates}
                />
              }
              <ChartExportButton chartTitle={figure.title} chartRef={chartRef} />
              <div ref={containerRef}>
                <HighchartsReact ref={chartRef} key={index} highcharts={Highcharts} options={chartOptions} />
              </div>
            </>
          }
        </div>
      {/* } */}

    </div>
  )
}, isNextChartEqualToPrev);

type InputStateHandler = {
  inputStates: Record<string, string>;
  setInputStates: React.Dispatch<React.SetStateAction<Record<string, string>>>;
}

const isNextFigureEqualToPrev = (prevProps, nextProps) => {
  const areEqual = JSON.stringify({
    ...prevProps,
    figure: prevProps.figure.caseIds
  }) === JSON.stringify({
    ...nextProps,
    figure: nextProps.figure.caseIds
  })
  // console.log('are figures equal?', areEqual);
  return areEqual;
}

export const Figure = React.memo(
  ({
    figure,
    extraChartOptions = {},
    arrayOfMultiFigureControls = [],
  }: {
    figure: FigureType;
    extraChartOptions: Record<string, unknown>;
    arrayOfMultiFigureControls: Array<Record<string, string>>;
  }) => {

    // const renderCount = React.useRef(0)

    const { isComparisonMode, comparisonCases, chartControlAllocation } = React.useContext(ModuleStateContext);

    const [isYAxisLocked, setIsYAxisLocked] = React.useState(true);

    // always create one input state handler per comparison result column (even if we're not using them), to avoid "fewer hooks than expected" error
    const inputStateHandlers = new Array(maxComparisonResultCols).fill(null).map(o => {
      const [inputStates, setInputStates] = useState<Record<string, string>>({});
      return {inputStates, setInputStates};
    }) as InputStateHandler[];

    // console.log(defaultInputStates)
    // we're using custom hook useMemoCompare here, which computes a memoized version of defaultInputStates, and only recalculates when JSON.stringify(prev) !== JSON.stringify(next) - this removed 3 extra re-renders for this and all child components
    const arrayOfMultiFigureControlsFinal = useMemoCompare(arrayOfMultiFigureControls, (prev, next) => {
      return JSON.stringify(prev) === JSON.stringify(next);
    })

    // console.log(inputStateHandlers.map(h => h.inputStates));

    useEffect(() => {

      // console.log('Figure > useEffect')
      // console.log(defaultInputStates, figure)

      inputStateHandlers?.forEach((stateHandler, index) => {
        // const defaultInputStatesFinal = (
        //   chartControlAllocation === 'group'
        //   ?
        //   arrayOfMultiFigureControlsFinal[0] // we're not using individual chart controls per chart anymore in comparison mode, even when comparing same case to itself, as per Ian's request
        //   :
        //   arrayOfMultiFigureControlsFinal[index]
        // );
        // const defaults = Object.keys(defaultInputStatesFinal).reduce(
        //   (acc: Record<string, string>, key: string) => {
        //     acc[key] = defaultInputStatesFinal[key];
        //     return acc;
        //   },
        //   {}
        // );

        stateHandler.setInputStates((prevInputStates) => {
          const newInputStates = {
            ...prevInputStates,
            // ...defaults,
          };

          // default to first option
          const figureDefaults = figure.inputs.reduce(
            (acc: Record<string, string>, input: FigureInput) => {
              if (newInputStates[input.name] === undefined) {
                acc[input.name] = input.options[0];
              }
              return acc;
            },
            {}
          );

          return {
            ...newInputStates,
            ...figureDefaults,
          };
        });
      })
    }, [JSON.stringify(arrayOfMultiFigureControlsFinal), figure]);

    // perform deep merge

    const seriesArray = comparisonCases?.map((comparisonCase, index) => {

      if (chartControlAllocation === 'individual') {
        // use first inputStateHandler, i.e. there's always one set of figure row controls now, rather than one-per-chart in individual mode, per Ian's request; but still use corresponding multi figure controls for this case column
        const inputStates = {
          ...inputStateHandlers[0].inputStates,
          ...arrayOfMultiFigureControlsFinal[index]
        }
        return figure.series(inputStates, index);
      } else if (chartControlAllocation === 'group') {
        // use one inputStateHandler (figure row controls) and one multi figure controls set in group mode
        const inputStates = {
          ...inputStateHandlers[0].inputStates,
          ...arrayOfMultiFigureControlsFinal[0]
        }
        return figure.series(inputStates, index)
      }
    })

    if (seriesArray && seriesArray.length > 1) {
      extraChartOptions.legend = merge(
        {
          align: 'center',
          verticalAlign: 'bottom',
          layout: 'horizontal',
          itemDistance: 10,
          itemMarginBottom: 10,
          symbolPadding: 3,
        },
        extraChartOptions.legend || {}
      )
    };

    const chartOptionsArray = seriesArray?.map(series => {
      if (!series) {
        return null;
      }

      return merge(
        {
          ...defaultChartOptions(figure.categories),
          series: series,
        },
        extraChartOptions,

      );
      // return merge(merged, figure.chartOptions)

    }) as ChartOptions[];

    const biggestYMaxes = useYAxisLocking(isYAxisLocked, chartOptionsArray);

    // console.log(chartOptionsArray)

    return (
      <React.Fragment>
        {/* <div className="py-1 px-2 bg-red-500 text-white">Figure rendered {(renderCount.current ++)} time(s)</div> */}
        <ComparisonRow
          sidebar={
            <div className="mt-2">
              <div className="mb-4">
                <Styles.Label className="mt-2 mb-4">{figure.title}</Styles.Label>
              </div>
              {/* {chartControlAllocation === 'group' &&  */}
                <div className="mb-4">
                  <FigureInputs
                    inputs={figure.inputs}
                    inputStates={inputStateHandlers[0].inputStates}
                    setInputStates={inputStateHandlers[0].setInputStates}
                    layout="row"
                  />
                </div>
              {/* } */}
              {isComparisonMode &&
                <YAxisToggle isYAxisLocked={isYAxisLocked} setIsYAxisLocked={setIsYAxisLocked} />
              }
            </div>
          }
          content={
            chartOptionsArray?.map((chartOptions, index) => {
              if (comparisonCases && comparisonCases[index].isLoading) {
                return (
                  <Styles.Loader key={index} />
                )
              } else {
                return (
                  <React.Fragment key={index}>
                    {!isComparisonMode &&
                      <Styles.Label className="my-2">{figure.title}</Styles.Label>
                    }
                    <Chart
                      key={index}
                      index={index}
                      chartOptions={chartOptions}
                      figure={figure}
                      showTitle={!isComparisonMode}
                      inputStateHandler={inputStateHandlers[index]}
                      yAxesMaxes={biggestYMaxes}
                      comparisonCaseId={comparisonCases?.[index]?.id}
                    />
                  </React.Fragment>
                )
              }
            })
          }
        />
      </React.Fragment>
    );
  }, isNextFigureEqualToPrev);
Figure.displayName = "Figure";

export const YAxisToggle = React.memo(({isYAxisLocked, setIsYAxisLocked}: {isYAxisLocked: boolean; setIsYAxisLocked: React.Dispatch<React.SetStateAction<boolean>>}) => {
  const { isComparisonMode, comparisonCases, chartControlAllocation } = React.useContext(ModuleStateContext) // TODO is this going to wreck benefits from memo HOC wrapper around this component?
  if (
    isComparisonMode
    &&
    comparisonCases?.filter(comparisonCase => !!comparisonCase?.data?.analysisResult)?.length > 1
    // &&
    // chartControlAllocation === 'group'
  ) {
    return <Toggle
      label="Lock Y Axes"
      value={isYAxisLocked}
      setValue={setIsYAxisLocked}
    />
    // return <(
    //   <div className="w-full my-3">
    //     <label className="flex items-center cursor-pointer">
    //       <div className="relative">
    //         <input type="checkbox" onChange={(e) => { setIsYAxisLocked(!isYAxisLocked) }} className="sr-only" />
    //         <div
    //           className={`block bg-gray-300 transition-colors ${isYAxisLocked ? 'bg-green-500' : ''} rounded-full`}
    //           style={{height: '22px', width: '42px'}}
    //         >
    //         </div>
    //         <div
    //           className={`absolute bg-white h-[18px] w-[18px] top-[2px] rounded-full transition-all left-[2px] ${isYAxisLocked ? 'left-[22px]' : ''}`}
    //           // style={isYAxisLocked ? {transform: 'translateX(100%)'} : {}}
    //           // style={{height: '20px', width: '20px', top: '2px', left: isYAxisLocked ? '20px' : '2px'}}
    //         >
    //         </div>
    //       </div>
    //       <Styles.Label className="ml-3">
    //         Lock Y Axes
    //       </Styles.Label>
    //     </label>

    //   </div>
    // )>
  } else {
    return null;
  }
})

const doesNextFigureSetEqualPrev = (prevProps, nextProps) => {
  // return false;
  let areEqual = nextProps?.figureSet?.caseIds?.every((id, index) => {
    return id === prevProps?.figureSet?.caseIds?.[index];
  });
  if (areEqual === undefined) {
    areEqual = false;
  }
  // console.log('figureSets are equal?', areEqual, prevProps?.figureSet?.caseIds, nextProps?.figureSet?.caseIds);
  return areEqual;
}

type ChartControlHandler = {
  inputStates: Record<string, string>;
  setInputStates: React.Dispatch<React.SetStateAction<{}>>;
}

export const FigureSet = //React.memo(
  ({
    figureSet,
    defaultInputs = {},
    chartControlHandlers,
    wrapInAccordion,
    accordionTitle,
  }: {
    figureSet: FigureSetType;
    defaultInputs?: Record<string, string>;
    chartControlHandlers?: ChartControlHandler[];
    wrapInAccordion?: boolean;
    accordionTitle?: string;
  }) => {

    if (!figureSet || !figureSet.figures) {
      // console.log('returning, b/c figureSet or figures are null')
      return null;
    }

    if (!chartControlHandlers) {
      chartControlHandlers = Array(maxComparisonResultCols).fill(null).map((o, comparisonIndex) => {
        const [inputStates, setInputStates] = useState(defaultInputs);
        return {inputStates, setInputStates};
      });
    }

    const { chartControlAllocation, comparisonCases } = React.useContext(ModuleStateContext);

    // const renderCount = React.useRef(0)

    // const inputStateHandlers = Array(maxComparisonResultCols).fill(null).map((o, comparisonIndex) => {
    //   const [inputStates, setInputStates] = useState(defaultInputs);
    //   return {inputStates, setInputStates};
    // })

    const figureSetControls = (
      <>
        {chartControlAllocation === 'individual'
          ?
          comparisonCases?.map((comparisonCase, comparisonIndex) => {
            const { inputStates, setInputStates } = chartControlHandlers[comparisonIndex];
            return (
              <FigureInputs
                inputs={figureSet.inputs}
                inputStates={inputStates}
                setInputStates={setInputStates}
                layout="row"
                key={[comparisonIndex, comparisonCases[comparisonIndex].id].join('_')}
              />
            )
          })
          :
          <FigureInputs
            inputs={figureSet.inputs}
            inputStates={chartControlHandlers[0].inputStates}
            setInputStates={chartControlHandlers[0].setInputStates}
            layout="row"
          />
        }
      </>
    )

    const html = (
      <React.Fragment>
        {/* <div className="py-1 px-2 bg-red-500 text-white">FigureSet rendered {(renderCount.current ++)} time(s)</div> */}

        {/* <div className="py-5 non-comparison-cell"> */}
        {/* <StickyFigureControls nonComparisonModeTop="2.49rem" comparisonModeTop="8.5rem"> */}
          {/* {figureSetControls} */}

        {/* </StickyFigureControls> */}

        <TiledColumn>
          {figureSet.figures.map((figure, i) => {
            return (
              <div key={i} className="w-full">
                <Figure
                  figure={figure}
                  extraChartOptions={figure.chartOptions || {}}
                  arrayOfMultiFigureControls={chartControlHandlers.map(handler => handler.inputStates)}
                />
              </div>
            );
          })}
        </TiledColumn>
      </React.Fragment>
    );

    if (wrapInAccordion) {
      return (
        <Accordion
          title={accordionTitle || ''}
          defaultOpen={true}
          stickyHeader={true}
          padContentTop={false}
          headerClassName="h-12"
          headerContentWhenOpen={
            figureSetControls
          }
          headerLayout="comparisonRow"
        >
          <div>
            {html}
          </div>
        </Accordion>
      )
    } else {
      return html;
    }

  }//, doesNextFigureSetEqualPrev
//);
FigureSet.displayName = "FigureSet";