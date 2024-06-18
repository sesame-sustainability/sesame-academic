import * as React from "react"
import Highcharts, { chart, ChartOptions } from "highcharts";
// import HighchartsBoost from 'highcharts/modules/boost';
import HighchartsReact from "highcharts-react-official";
import merge from "deepmerge";
import { ChartSubtitle, ChartTitle, Loader } from "../styles";
import { Dataset, Series, defaultChartOptions, YAxisToggle, isNextChartEqualToPrev, resizeChart } from "../figures";
import { ChartExportButton } from "../chartExportButton";
import { Select, Label } from "../styles"
import { ComparisonRow, getCaseNameFromComparisonCaseAtIndex, ModuleStateContext } from "../comparableResultsModule";
import { maxComparisonResultCols } from "../../utils/constants";
import { getMaxOfSeriesArray, getMinOfSeriesArray, useYAxisLocking } from "../../hooks/useYAxisLocking";
import { useChartResizing } from "../../hooks/useChartResizing";
import { isBrowser } from "../../utils";

// if (isBrowser()) {
//   HighchartsBoost(Highcharts);
// }

const MultiDatasetUnitDropdown = ({
  dataset,
  relativeUnit,
  percentUnit,
  units,
  value,
  onChange,
  ...props
}: {
  dataset: Dataset | null;
  relativeUnit: string;
  percentUnit?: string | null;
  units?: Record<string, string>;
  value: string;
  onChange: (val: string) => void;
}): JSX.Element => {
  let unit = null;
  if (dataset) {
    if (dataset.unit) {
      unit = dataset.unit;
    } else {
      unit = units?.[dataset.label];
    }
  }

  const scalarUnit = dataset?.scalarUnit;

  let options: { label: string; value: string }[] = [];
  if (dataset) {
    options.push({ label: `(${unit})`, value: "raw" });
    if (scalarUnit) {
      options.push({ label: `(${scalarUnit})`, value: "scaled" });
    }
    if (relativeUnit) {
      options.push({ label: `(${relativeUnit})`, value: "relative" })
    }
    if (percentUnit) {
      options.push({ label: `(${percentUnit})`, value: "relative%" })
    }
  }

  // set unit back to default value when scalarUnit is cleared
  React.useEffect(() => {
    if (!scalarUnit) {
      onChange('raw');
    }
  }, [scalarUnit])

  return (
    <Select
      {...props}
      value={value}
      onChange={(e) => {
        onChange(e.target.value);
      }}
    >
      {options.map((option, i) => (
        <option key={i} value={option.value}>
          {option.label}
        </option>
      ))}
    </Select>
  );
};

type MultiDatasetChartControlHandler = {
  primaryOutput: string;
  setPrimaryOutput: React.Dispatch<React.SetStateAction<string>>;
  secondaryOutput: string | undefined;
  setSecondaryOutput: React.Dispatch<React.SetStateAction<string | undefined>>;
  primaryUnit: string;
  setPrimaryUnit: React.Dispatch<React.SetStateAction<string>>;
  secondaryUnit: string;
  setSecondaryUnit: React.Dispatch<React.SetStateAction<string>>;
}

const MultiDatasetChartControls = ({
  comparisonIndex,
  chartControlHandler,
  prototypeDatasets,
  primaryDataset,
  // secondaryDataset,
  showSecondarySeriesOnly,
  // chartControlAllocation,
  units,
  relativeYear,
  layout,
}: {
  comparisonIndex: number;
  chartControlHandler: MultiDatasetChartControlHandler;
  prototypeDatasets: Dataset[] | undefined;
  primaryDataset: Dataset;
  // secondaryDataset?: Dataset;
  showSecondarySeriesOnly: boolean;
  // chartControlAllocation: string;
  units: Record<string, string>;
  relativeYear: number | undefined;
  layout: 'column' | 'row';
}) => {
  const {
    primaryOutput, setPrimaryOutput,
    secondaryOutput, setSecondaryOutput,
    primaryUnit, setPrimaryUnit,
    secondaryUnit, setSecondaryUnit,
  } = chartControlHandler;
  let secondaryDataset = null;
  if (chartControlHandler.secondaryOutput !== undefined) {
    secondaryDataset = (prototypeDatasets?.filter((dataset) => dataset.axis === 1) || []).find(d => d.id === chartControlHandler.secondaryOutput)
  }

  // only show "share" unit option when there's more than one column in the data
  const showShareUnitOnPrimaryDataset = primaryDataset?.columns?.length > 2; // single-column datasets will still have two "columns", since the first "column" is just the x-axis label, and the 2nd+ columns are actually data columns
  
  return (
    <div className={`grid gap-4 my-2 ${layout === 'row' ? 'grid-cols-2' : ''}`}>
      {!showSecondarySeriesOnly &&
        <div className="flex-1">
          <Select
            onChange={(e) => {
              setPrimaryOutput(e.target.value);
            }}
            value={primaryOutput}
            className="mb-1"
          >
            {prototypeDatasets && prototypeDatasets
              .filter((dataset) => dataset.axis === 0)
              .map((dataset, i) => (
                <option key={i} value={dataset.id}>
                  {dataset.label}
                </option>
              ))}
          </Select>
          <MultiDatasetUnitDropdown
            dataset={primaryDataset}
            relativeUnit={showShareUnitOnPrimaryDataset ? "share" : ''}
            value={primaryUnit}
            onChange={setPrimaryUnit}
          />
        </div>
      }
      <div className="flex-1">
        <Select
          onChange={(e) => {
            const val = e.target.value;
            // let plotIndex = undefined;
            // if (val !== "") {
            //   plotIndex = parseInt(val);
            // }
            setSecondaryOutput(val);
          }}
          value={secondaryOutput}
          className="mb-1"
        >
          <option value=""></option>
          {prototypeDatasets && prototypeDatasets
            .filter((dataset) => dataset.axis === 1)
            .map((dataset, i) => (
              <option key={i} value={dataset.id}>
                {dataset.label}
              </option>
            ))}
        </Select>
        <MultiDatasetUnitDropdown
          dataset={secondaryDataset}
          relativeUnit={relativeYear ? `relative to ${relativeYear}` : ''}
          percentUnit={relativeYear ? `% change from ${relativeYear}` : null}
          units={units}
          value={secondaryUnit}
          onChange={setSecondaryUnit}
        />
      </div>
    </div>
  )
}

const MultiDatasetChart = React.memo(({
  comparisonIndex,
  comparisonCaseId,
  chartOptions,
  // chartControlAllocation,
  // chartControls,
  title,
  isYAxisMinZero = true,
  yAxesMaxes,
}: {
  comparisonIndex: number;
  comparisonCaseId: number;
  chartOptions: ChartOptions | null;
  // chartControlAllocation: string;
  // chartControls: JSX.Element;
  title?: string;
  isYAxisMinZero?: boolean;
  yAxesMaxes?: Array<number | null>;
}) => {
  const chartRef = React.useRef(null);
  const containerRef = React.useRef(null);
  // useChartResizing({chartRef, containerRef, deps: [JSON.stringify(chartOptions), yAxesMaxes]});

  // const renderCount = React.useRef(0);

  React.useEffect(() => {
    chartRef.current?.chart?.yAxis?.[0]?.setExtremes(0, yAxesMaxes?.[0] || null);
    chartRef.current?.chart?.yAxis?.[1]?.setExtremes(isYAxisMinZero ? 0 : null, yAxesMaxes?.[1] || null);
  }, [yAxesMaxes]);

  // const handleResize = () => {
  //   console.log('resize');
  //   resizeChart(chartRef.current?.chart)
  // }

  // React.useEffect(() => {
  //   const chart = chartRef.current?.chart;
  //   resizeChart(chart);
  // }, [JSON.stringify(chartOptions)])

  // React.useEffect(() => {
  //   document.addEventListener('resize', handleResize);
  //   return () => {
  //     document.addEventListener('resize', handleResize);
  //   };
  // });

  // console.log(chartOptions)

  return (
    <div className="my-2">
      {/* <div className="py-1 px-2 bg-red-500 text-white">MultiDatasetChart rendered {(renderCount.current ++)} time(s)</div> */}

      {chartOptions &&
        <>
          {/* {chartControlAllocation === 'individual' &&
            <div className="mt-2 mb-3">
              {chartControls}
            </div>
          } */}
          <div className="pt-2 relative">
            <ChartExportButton chartTitle={title} chartRef={chartRef} />
            <div ref={containerRef}>
              <HighchartsReact
                ref={chartRef}
                key={comparisonIndex}
                highcharts={Highcharts}
                options={chartOptions}
              />
            </div>
          </div>
        </>
      }
    </div>
  )
}, isNextChartEqualToPrev);

// const isNextFigureEqualToPrev = (prevProps, nextProps) => {
//   const areEqual = JSON.stringify({
//     ...prevProps,
//     figure: prevProps.figure.caseIds
//   }) === JSON.stringify({
//     ...nextProps,
//     figure: nextProps.figure.caseIds
//   })
//   console.log('are figures equal?', areEqual);
//   return areEqual;
// }

const roundVal = (val: number | null) => {
  if (val === null) {
    return null;
  }

  if (Math.abs(val) < 0.00000001) {
    return 0;
  } else {
    return val;
  }
};

const normalizeSeries = (series: Series[]) => {
  // percentage of total
  if (!series[0]?.data) return;
  for (let i = 0; i < series[0].data.length; i++) {
    const total = series.map((s) => s.data[i]).reduce((a, b) => a + b, 0);
    series.forEach((s, seriesIndex) => {
      const isTotalZeroAtThisDataPoint = total === 0;
      const newVal = isTotalZeroAtThisDataPoint ? null : (s.data[i] / total) * 100; // don't show any % share values if total of all series at this data point is zero (pass null to charts)
      series[seriesIndex].data[i] = typeof s.data[i] === 'number' ? newVal : null
    });
  }
};

const makeSeriesRelativeToYear = (series: Series[], year: number, categories: number[]) => {
  const idxOfYear = categories?.indexOf(year);
  series.forEach((s, seriesIndex) => {
    const valAtYear = s.data[idxOfYear];
    series[seriesIndex].data = s.data.map(d => d / valAtYear);
  });
};

const makeSeriesPercentChange = (series: Series[]) => {
  series.forEach((s, seriesIndex) => {
    series[seriesIndex].data = s.data.map(d => (d - 1) * 100);
  })
};

const makeSeriesRelativeToAvg = (series: Series[]) => {
  series.forEach((s, seriesIndex) => {
    const sum = s.data.reduce((sum, val) => sum + val, 0);
    const avg = sum / s.data.length;
    series[seriesIndex].data = s.data.map(value => value / avg);
  });
};

const makeSeriesRelativeToMax = (series: Series[]) => {
  series.forEach((s, seriesIndex) => {
    const max = s.data.reduce((max, val) => Math.max(max, val), 0);
    series[seriesIndex].data = s.data.map(value => value / max);
  });
};

const scaleSeriesByScalar = (series: Series[], scalar: number = 1) => {
  if (scalar !== 1) {
    series.forEach((s, seriesIndex) => {
      series[seriesIndex].data = s.data.map(value => value * scalar);
    })
  }
}

export const slugifyString = (string: string) => {
  return string.toLowerCase().replace(/[^A-Za-z0-9 -]/gi, '')
}

export const MultiDatasetFigure = React.memo(
  ({
    datasetsByCase,
    // analysisResults,
    colors = {},
    units = {},
    order = [],
    chartOptionsByCase = [],
    showInLegend = {},
    defaultPrimaryOutput = '',
    defaultSecondaryOutput = undefined,
    display = (name: string) => name,
    isYears = true,
    defaultZoom = null,
    defaultUnit = null,
    scaleAxes = false,
    primaryChartTypes,
    showSecondarySeriesOnly = false,
    showAllCasesOnOneChart = false,
    summaryGraphUnit,
    title,
    relativeYear = 2019,
  }: {
    datasetsByCase?: Array<Dataset[]>;
    // analysisResults,
    colors?: Record<string, string>;
    units?: Record<string, string>;
    order?: string[];
    chartOptionsByCase?: Array<Record<string, unknown>>;
    showInLegend?: Record<string, boolean>;
    defaultPrimaryOutput?: string;
    defaultSecondaryOutput?: string | undefined;
    display?: (name: string) => string;
    isYears?: boolean;
    defaultZoom?: null | number;
    defaultUnit?: null | string;
    scaleAxes?: boolean;
    primaryChartTypes?: Array<string | undefined>;
    showSecondarySeriesOnly?: boolean;
    showAllCasesOnOneChart?: boolean;
    summaryGraphUnit?: string;
    title?: string;
    relativeYear: number;
  }) => {

    if (!datasetsByCase) {
      return null;
      // throw new Error('No dataset arrays provided!');
    }

    const arrayOfChartControlHandlers = new Array(maxComparisonResultCols).fill(null).map(o => {
      const [primaryOutput, setPrimaryOutput] = React.useState<string>(defaultPrimaryOutput);
      const [secondaryOutput, setSecondaryOutput] = React.useState<string | undefined>(defaultSecondaryOutput);

      const [primaryUnit, setPrimaryUnit] = React.useState("million");
      const [secondaryUnit, setSecondaryUnit] = React.useState(summaryGraphUnit || "raw");
      return {
        primaryOutput, setPrimaryOutput,
        secondaryOutput, setSecondaryOutput,
        primaryUnit, setPrimaryUnit,
        secondaryUnit, setSecondaryUnit,
      }
    }) as MultiDatasetChartControlHandler[];

    const [isYAxisLocked, setIsYAxisLocked] = React.useState(true);

    const { isComparisonMode, comparisonCases, chartControlAllocation } = React.useContext(ModuleStateContext) // TODO is this going to wreck benefits from memo HOC wrapper around this component?

    datasetsByCase = datasetsByCase?.map(datasets => datasets?.map(dataset => {
      return {
        ...dataset,
        id: slugifyString(dataset.label)
      }
    }))

    // don't render a chart if the specified default primary output doesn't exist in the chart data of any cases
    if (defaultPrimaryOutput) {
      const isPrimaryOutputInAnyComparisonCase = datasetsByCase.some(datasets => {
        return datasets?.some(d => d.id === defaultPrimaryOutput)
      })
      if (!isPrimaryOutputInAnyComparisonCase) {
        return null;
      }
    }

    const primaryDatasetsByCase = datasetsByCase.map(
      datasets => datasets?.filter((dataset) => dataset.axis === 0) || []
    );
    const secondaryDatasetsByCase = datasetsByCase.map(
      datasets => datasets?.filter((dataset) => dataset.axis === 1) || []
    );

    const createArrayOfChartOptions = (): Array<ChartOptionsWithSeries | null> | undefined => {

      // there is one dataset array per comparison case column

      const arrayOfChartOptions = datasetsByCase?.map((datasets, comparisonIndex) => {

        // if group mode, use only the first chartControlHandler to control all charts in a row
        // const chartControlHandlerIndex = chartControlAllocation === 'group' ? 0 : comparisonIndex;
        const chartControlHandlerIndex = 0; // we're not using individual chart controls per chart anymore when comparing same case, per Ian's request - only one set of controls per row
        const {primaryOutput, secondaryOutput, primaryUnit} = arrayOfChartControlHandlers[chartControlHandlerIndex];
        const secondaryUnit = showAllCasesOnOneChart ? summaryGraphUnit : arrayOfChartControlHandlers[chartControlHandlerIndex].secondaryUnit;

        if (!datasets || !datasets.length) {
          return null;
        }

        let primaryDataset = primaryDatasetsByCase[comparisonIndex].find(d => d.id === primaryOutput) || primaryDatasetsByCase[comparisonIndex]?.[0];
        // if (primaryOutput && !primaryDataset) {
        //   return null;
        // } else if (!primaryDataset) {
        //   primaryDataset = 
        // }
        

        const categories = primaryDataset?.data?.map((item) => item[0]);
        // const chartType = primaryDataset.type;

        const primarySeries = primaryDataset?.columns
          .slice(1)
          .map((name, i) => {
            // TODO: this is for fleet data that should really be updated on the backend
            name = (name || primaryDataset.label).replace(/^S_/, "");

            let show = showInLegend[name];
            if (show === undefined) {
              show = true;
            }

            let chartType = primaryChartTypes?.[comparisonIndex] || 'area';
            let dashStyle = 'Solid';
            if (primaryDataset.seriesStyles) {
              // override style per series if specified
              const style = primaryDataset.seriesStyles[name];
              if (style === 'dashed-line') {
                chartType = 'line';
                dashStyle = 'Dash';
              }
            }

            return {
              _name: name,
              name: display(name),
              color: colors[name],
              yAxis: 0,
              type: chartType,
              stacking: (chartType === 'area' || chartType === 'column') ? 'normal' : undefined,
              data: primaryDataset?.data?.map((item) => roundVal(item[i + 1])),
              showInLegend: show,
              dashStyle: dashStyle,
            };
          })
          .sort((a, b) => {
            if (order) {
              const ai = order.indexOf(a._name);
              const bi = order.indexOf(b._name);
              return ai - bi;
            } else {
              return 0;
            }
          });


        const defaults = defaultChartOptions(categories, isYears);

        if (primaryUnit.startsWith("relative")) {
          normalizeSeries(primarySeries);
          defaults.yAxis[0].tickAmount = 7; // Tick on multiples of 20
          defaults.yAxis[0].max = 120;
        } else if (primaryUnit === 'scaled') {
          scaleSeriesByScalar(primarySeries, primaryDataset.scalar);
        } else if (primaryDataset.unit?.includes('%')) {
          scaleSeriesByScalar(primarySeries, 100)
        }

        let series: Series[] = !showSecondarySeriesOnly ? primarySeries : [];

        let secondaryDataset: Dataset | undefined;
        if (secondaryOutput !== undefined) {
          secondaryDataset = secondaryDatasetsByCase[comparisonIndex].find(d => d.id === secondaryOutput);

          const isPrimarySeriesCumulative = !!primaryDataset.label.match(/since|cumulative/gi);
          const isSecondarySeriesCumulative = !!secondaryDataset?.label.match(/since|cumulative/gi);
          const shouldPlotSecondarySeriesOnPrimaryAxis = (
            (primaryUnit === secondaryUnit && !primaryUnit.startsWith('relative')) // avoid case where
            &&
            secondaryDataset?.unit === primaryDataset.unit
            &&
            isPrimarySeriesCumulative === isSecondarySeriesCumulative
          )

          if (shouldPlotSecondarySeriesOnPrimaryAxis) {
            defaults.yAxis = defaults.yAxis.slice(0, 1) // remove unused right Y axis if we're plotting secondary dataset on left axis
          }

          const secondarySeries = secondaryDataset?.columns
            .slice(1)
            .map((name, i) => ({
              name: secondaryDataset?.label || "",
              yAxis: shouldPlotSecondarySeriesOnPrimaryAxis ? 0 : 1,
              type: "line",
              color: "#FF0000",
              data: secondaryDataset?.data?.map((item) => roundVal(item[i + 1])) || [],
              showInLegend: false,
            }));

          if (secondaryDataset && secondarySeries) {
            if (secondaryUnit?.startsWith("relative")) {
              if (isYears) {
                makeSeriesRelativeToYear(secondarySeries, relativeYear, categories);
                if (secondaryUnit === "relative%") {
                  makeSeriesPercentChange(secondarySeries);
                }
              } else if (secondarySeries[0].name === "Storage energy") {
                // Special case - relative to max
                // not sure if there's a better way to handle this
                makeSeriesRelativeToMax(secondarySeries);
              } else {
                makeSeriesRelativeToAvg(secondarySeries);
              }
            } else if (secondaryUnit === 'scaled') {
              scaleSeriesByScalar(secondarySeries, secondaryDataset.scalar);
            } else if (secondaryDataset.unit?.includes('%')) {
              scaleSeriesByScalar(secondarySeries, 100)
            }
            series = (series || []).concat(secondarySeries);
          }

        }

        // if (showAllCasesOnOneChart)
        //   console.log(series)

        const min = 0;

        const seriesToUseForMaxCalculation = defaults.yAxis.length > 1 ? primarySeries : series; // if using only one Y axis, calculate max from all series; else only use primary series
        const primaryMax = getMaxOfSeriesArray(seriesToUseForMaxCalculation); // this function properly accounts for stacked series, and gives a tighter-hugging max than Highcharts does by default, which reduces whitespace
        defaults.yAxis[0].tickAmount = 7;
        defaults.yAxis[0].min = min;
        defaults.yAxis[0].max = primaryMax;

        // figure out if we should lock left and right axes
        if (
          scaleAxes
          &&
          primaryDataset.unit === secondaryDataset?.unit
          &&
          primaryUnit === secondaryUnit
          &&
          series.some(series => series.yAxis === 1)
          &&
          !!defaults.yAxis[1]
        ) {
          // scale right Y axis to match left Y axis
          defaults.yAxis[1].tickAmount = 7;
          defaults.yAxis[1].min = min;
          defaults.yAxis[1].max = primaryMax;
        }

        if (showSecondarySeriesOnly) {
          defaults.yAxis[1].opposite = false;
        }

        if (!secondaryDataset) {
          defaults.yAxis = [defaults.yAxis[0]];
        }

        if (defaults.yAxis.length > 1) {
          defaults.yAxis[1].min = getMinOfSeriesArray(series);
        }

        // defaults.yAxis[0].tickAmount = undefined;
        // defaults.yAxis[0].tickPixelInterval = 22;

        return merge(
          {
            ...defaults,
            series,
          },
          chartOptionsByCase?.[comparisonIndex] || {}
        ) as ChartOptions;
      });

      if (showAllCasesOnOneChart) {
        const summaryGraphLineColors = ['#000', '#4CA8BD', '#FA8334']
        const prototypeCaseChartOptions = arrayOfChartOptions.find(chartOptions => !!chartOptions);
        let chartOptions = {
          ...prototypeCaseChartOptions,
          series: arrayOfChartOptions.map((options, comparisonIndex) => {
            return {
              ...options?.series?.[0],
              color: summaryGraphLineColors[comparisonIndex],
              showInLegend: !!options, // hide from legend if case data does not exist yet (case has not been run)
              name: getCaseNameFromComparisonCaseAtIndex(comparisonCases?.[comparisonIndex], comparisonIndex),
            }
          }).filter(options => !!options?.showInLegend),
        }
        if (chartOptions.yAxis?.[0]) {
          chartOptions.yAxis[0].visible = false; // hide unused primary (left) Y axis (we're only using secondary (right) Y axis in summary graphs, but moving it to left side)
        }
        if (chartOptions.yAxis?.[1]) {
          delete chartOptions.yAxis?.[1].labels.style.color; // get rid of red color which is default for MultiDatasetFigure right axis (axis 1)
        }
        return [chartOptions];
      } else {
        return arrayOfChartOptions;
      }
    }

    // just find one dataset that exists in comparison array, to base units, etc. off of (doesn't matter which one it is, all comparison charts should have the same units)
    const prototypeDatasets = datasetsByCase.find(datasets => {
      return datasets && datasets.length > 0
    });
    const primaryDatasets = prototypeDatasets?.filter((dataset) => dataset.axis === 0) || []
    const primaryDataset = primaryDatasets.find(dataset => dataset.id === arrayOfChartControlHandlers[0].primaryOutput) || primaryDatasets?.[0]

    const getSecondaryDatasetUnitByOutput = (outputId: string | undefined) => {
      if (typeof(outputId) === 'string') {
        return secondaryDatasetsByCase.find(arr => !!arr.length)?.find(dataset => dataset.id === outputId)?.unit;
      }
    }

    let arrayOfChartOptions = createArrayOfChartOptions();

    const biggestYMaxes = useYAxisLocking(isYAxisLocked, arrayOfChartOptions);

    if (!(prototypeDatasets && prototypeDatasets.length > 0)) {
      return null;
    }

    if (showAllCasesOnOneChart) {
      const unitToDisplay = summaryGraphUnit === 'relative' ? 'Rel. to 2019' : getSecondaryDatasetUnitByOutput(defaultSecondaryOutput);
      return (
        <div className="">
          <div>
            <ChartSubtitle>
              <b className="mr-2">{title}</b>
              <span className="text-gray-500 text-base">({unitToDisplay})</span>
            </ChartSubtitle>
          </div>
          <MultiDatasetChart
            // key={comparisonIndex} // TODO make this unique for better render performance?
            chartOptions={arrayOfChartOptions?.[0]}
            comparisonIndex={0}
            // comparisonCaseId={null}
            title={title}
            yAxesMaxes={biggestYMaxes}
            isYAxisMinZero={arrayOfChartControlHandlers?.[0].secondaryUnit !== "relative%"}
            chartControlAllocation={chartControlAllocation}
            // title={primaryDataset.label}
          />
        </div>
      )
    } else { // normal multidataset charts (not summary graphs)
      return (
        <ComparisonRow
          className={'h-full'}
          sidebar={
            <>
              <MultiDatasetChartControls
                comparisonIndex={0}
                chartControlHandler={arrayOfChartControlHandlers[0]}
                prototypeDatasets={prototypeDatasets}
                primaryDataset={primaryDataset}
                showSecondarySeriesOnly={showSecondarySeriesOnly}
                layout="column"
                relativeYear={isYears ? relativeYear : undefined}
                units={units}
              />
              {isComparisonMode &&
                <YAxisToggle isYAxisLocked={isYAxisLocked} setIsYAxisLocked={setIsYAxisLocked} />
              }
            </>
          }
          content={
            arrayOfChartOptions?.map((chartOptions, comparisonIndex) => {
              if (comparisonCases && comparisonCases[comparisonIndex].isLoading) {
                return (
                  <Loader key={comparisonIndex} />
                )
              } else {
                const comparisonCaseId = comparisonCases?.[comparisonIndex]?.id;
                return (
                  <div key={comparisonIndex}>
                    {!isComparisonMode && comparisonCaseId &&
                      <div className="mt-3 mb-3">
                        <MultiDatasetChartControls
                          comparisonIndex={comparisonIndex}
                          chartControlHandler={arrayOfChartControlHandlers[comparisonIndex]}
                          prototypeDatasets={prototypeDatasets}
                          primaryDataset={primaryDataset}
                          // secondaryDataset={secondaryDatasetsByCase}
                          showSecondarySeriesOnly={showSecondarySeriesOnly}
                          units={units}
                          relativeYear={isYears ? relativeYear : undefined}
                          layout="row"
                        />
                      </div>
                    }
                    <MultiDatasetChart
                      key={comparisonIndex} // TODO make this unique for better render performance?
                      chartOptions={chartOptions}
                      comparisonIndex={comparisonIndex}
                      comparisonCaseId={comparisonCaseId}
                      isYAxisMinZero={arrayOfChartControlHandlers[comparisonIndex].secondaryUnit !== "relative%"}
                      yAxesMaxes={biggestYMaxes}
                      chartControlAllocation={chartControlAllocation}
                      title={primaryDataset.label}
                    />
                  </div>
                )
              }
            })
          }
        />
      )
    }
  }
)
MultiDatasetFigure.displayName = "MultiDatasetFigure";