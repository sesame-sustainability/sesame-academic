import React, { useState, useRef, useEffect, useCallback, useMemo, SetStateAction } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

import * as Styles from "../styles";
import Layout from "../layout";
import useAppMetadata from "../../hooks/useAppMetadata";
import { roundToHundredth, colors, sumArray } from "../../utils";
import { Dataset, valueFormatter, chartColors } from "../figures";
import { MultiDatasetFigure } from "../graphs/multiDatasetFigure";
import { ComparisonRow, ModuleStateContext } from "../comparableResultsModule";
import { maxComparisonResultCols } from "../../utils/constants";
import { useWidth } from "../../hooks/useChartResizing";
import Accordion from "../accordion";
import { ComparisonInputHandler } from "../inputHandler";
import { useSetting } from "../../hooks/useSettings";
import { customAlert } from "../customAlert";
import { navigate } from "gatsby";
import { atom, useAtom } from "jotai";
import { PowerGreenfieldBarFigs } from "../graphs/powerGreenfieldBarFigs";

type AnalysisResult = {
  CPC: number;
  DPC: number;
  EC: number;
  d: number;
  f_DD: number;
  f_DVS: number;
  f_LIS: number;
  f_curtail: number;
  G_demand: number[];
  G_storage: number[];
  G_curtailed: number[];
  G_wind: number[];
  G_solar: number[];
  D_gen: number[];
  D_storage: number[];
  D: number[];
  G: number[];
  G_minus_D: number[];
  P_storage: number[];
  E_storage: number[];
};

export const areaChartColors = {
  "Curtailment": colors.black,
  "Curtail": colors.black,
  "Storage": chartColors.indigo_light,
  "Demand": colors.green,
  "Wind": colors.green,
  "Solar": colors.yellow,
  "Solar & Wind": colors.green,
  "Solar wind nuclear": colors.green,
  "Nuclear": colors.orange,
  "Generation": colors.green,
  "Natural gas": colors.black,
  "Demand direct": colors.green,
  "Demand via storage": chartColors.indigo_light,
  "TD loss": colors.gray,
  "Storage loss": colors.orange,
};

const lineChartColors = {
  "Demand": colors.blue,
  "Generation": colors.blue,
  "Generation - demand": colors.blue,
  "Solar generation": colors.blue,
  "Wind generation": colors.blue,
  "Storage power": colors.blue,
  "Storage energy": colors.blue,
};

const lineChartLegend = {
  "Demand": false,
  "Generation": false,
  "Generation - demand": false,
  "Solar generation": false,
  "Wind generation": false,
  "Storage power": false,
  "Storage energy": false,
};

export const powerGreenfieldDemandSizeAtom = atom('')

const PPS = (): JSX.Element => {

  const { pps: { pps: ppsMetadata } } = useAppMetadata();
  const { isComparisonMode, comparisonCases } = React.useContext(ModuleStateContext);
  const [demandSize, setDemandSize] = useAtom(powerGreenfieldDemandSizeAtom);

  const [isNonCommercialUser, setIsNonCommercialUser] = useSetting('isNonCommercialUser');

  React.useEffect(() => {

    if (isNonCommercialUser === false) {
      customAlert({
        type: 'confirm',
        message: <div className="space-y-2">
          <div>Power Greenfield uses an academic license for Gurobi, which is not available for commercial users.</div>
          <div>Are you a <b>non-commercial</b> user?</div>
        </div>,
        confirmButtonText: 'Yes, I am a non-commercial user. Proceed.',
        cancelButtonText: 'No, I am a commercial user. Return to homepage.',
        onConfirm: () => {
          setIsNonCommercialUser(true);
        },
        onCancel: () => {
          navigate('/app')
        },
        dismissable: false,
      })
    }
  }, [isNonCommercialUser])

  const areAnyChartsLoaded = comparisonCases?.some(comparisonCase => !!comparisonCase?.data?.analysisResult)

  return (
    <Layout
      resultsRibbonContent={
        areAnyChartsLoaded ? <DemandSizeControls demandSize={demandSize} setDemandSize={setDemandSize} /> : undefined
      }
      secondCol={isNonCommercialUser ? [<Figures demandSize={demandSize} />] : []}
    >
      {isNonCommercialUser &&
        <ComparisonInputHandler moduleMetadata={ppsMetadata} />
      }
    </Layout>
  );
};

export default PPS;

const DemandSizeControls = ({
  demandSize,
  setDemandSize
}: {
  demandSize: string;
  setDemandSize: React.Dispatch<SetStateAction<string>>
}) => {
  // const { demandSize, setDemandSize } = chartControlHandler;
  const demandSizeOptions = [
    '1 kW, ~1 US home',
    '1 GW, ~1 large US city',
    '10 GW, ~1 US state',
    '100 GW, ~1 US NERC region',
  ]
  return (
    <div className="h-full flex items-center">
    <div className="flex flex-row">
      <div className="flex flex-row mr-4">
        <Styles.Label className="mr-2 flex-shrink-0">Average demand:</Styles.Label>
        <Styles.Select
          onClick={(e) => {
            e.stopPropagation(); // prevent toggling accordion
          }}
          onChange={(e) => {
            const newDemandSize = e.target.value;
            setDemandSize(newDemandSize);
          }}
          value={demandSize}
        >
          <option value="" label="Not given" />
          {demandSizeOptions.map((option, index) => {
            return (
              <option key={index} value={option} label={option} />
            );
          })}
        </Styles.Select>
      </div>
      {/* <div className="flex flex-row">
        <Styles.Label className="mr-2">Period:</Styles.Label>
        <Styles.Select
          onChange={(e) => {
            const val = e.target.value;
            setTimePeriod(val);
          }}
          value={timePeriod}
        >
          <option value="day">day</option>
          <option value="week">week</option>
          <option value="month">month</option>
          <option value="quarter">quarter</option>
          <option value="year">year</option>
        </Styles.Select>
      </div> */}
    </div>
  </div>
  )
}

const startOfMonths = [
  0, // Jan 1
  31, // Feb 1
  59, // March 1
  90, // April 1
  120, // May 1
  151, // June 1
  181, // July 1
  212, // Aug 1
  243, // Sept 1
  273, // Oct 1
  304, // Nov 1
  334, // Dec 1
];

const dayToDate = (day: number): string => {
  // day is 0-indexed
  const year = new Date(2021, 0); // any year that is not a leap year will do
  const date = new Date(year.setDate(day + 1)); // date day needs to be 1-indexed

  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const month = months[date.getMonth()];
  return `${month.slice(0,3)}-${date.getDate()}`;
};

const HourlyFigureControls = ({
  chartControlHandler
}: {
  chartControlHandler: PowerGreenfieldChartControlHandler
}) => {
  const {startDay, setStartDay, timePeriod, setTimePeriod, timeStep, setTimeStep} = chartControlHandler;
  
  const timePeriodIndex = timeStepOptions.indexOf(timePeriod)
  const timeStepIndex = timeStepOptions.indexOf(timeStep)

  // update timeStep when timePeriod changes, to make sure timeStep is always at least 1 step more granular than timePeriod (otherwise we'd be in pie or bar chart territory, with only one x-axis value)
  React.useEffect(() => {
    if (timeStepIndex >= timePeriodIndex) {
      setTimeStep(timeStepOptions[timePeriodIndex > 0 ? timePeriodIndex - 1 : 0])
    }
  }, [timePeriod, timeStep])

  // filter time step options based on current time period
  const timeStepOptionsFiltered = timeStepOptions.slice(0, timePeriodIndex)

  return (
    <div className="h-full flex items-center">
      <div className="flex flex-row">
        <div className="flex flex-row space-x-2">
          <Styles.Label className="flex-shrink-0">Start</Styles.Label>
          <Styles.Select
            onChange={(e) => {
              const val = parseInt(e.target.value);
              setStartDay(val);
            }}
            value={startDay}
          >
            {
              startOfMonths.map(day => {
                return (
                  <option key={day} value={day}>
                    {dayToDate(day)}
                  </option>
                );
              })
            }
          </Styles.Select>
          <Styles.Label className="flex-shrink-0 pl-2">Period</Styles.Label>
          <Styles.Select
            onChange={(e) => {
              const val = e.target.value;
              setTimePeriod(val);
            }}
            value={timePeriod}
          >
            <option value="day">day</option>
            <option value="week">week</option>
            <option value="month">month</option>
            <option value="quarter">quarter</option>
            <option value="year">year</option>
          </Styles.Select>
          <Styles.Label className="flex-shrink-0 pl-2">Timestep</Styles.Label>
          <Styles.Select
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              setTimeStep(e.target.value)
            }}
          >
            {timeStepOptionsFiltered.map(option => (
              <option value={option} label={option} />
            ))}
          </Styles.Select>
        </div>
      </div>
    </div>
  )
}

export const parseDemandSize = (demandSize: string) => {
  const demandSizeValueWithUnit = demandSize?.split(',')?.[0];
  const [demandSizeValueString, demandSizeUnit] = demandSizeValueWithUnit?.split(' ');
  const demandSizeValue = demandSizeValueString ? parseFloat(demandSizeValueString) : 1;
  return { demandSizeValue, demandSizeUnit };
}

const GenerationChart = ({
  comparisonIndex,
  demandSize,
}: {
  comparisonIndex: number;
  demandSize: string;
}) => {
  const { comparisonCases, isComparisonMode } = React.useContext(ModuleStateContext);
  const analysisResult = comparisonCases?.[comparisonIndex]?.data?.analysisResult;
  const containerRef = React.useRef(null);
  const chartRef = React.useRef(null);

  const width = useWidth(containerRef);
  // const legendHeight = width && width < 300 ? 160 : 90; // for bar chart
  const legendHeight = 0;
  // const chartHeight = 80; // bar chart height
  // const chartHeight = width ? width * 0.6;
  const height = width ? width * 0.50 + legendHeight : '50%';

  if (!analysisResult) return null;
  return (
    <div ref={containerRef}>
      <div className={`py-3 text-lg font-bold text-gray-700`}>% of generation</div>
      <HighchartsReact
        ref={chartRef}
        highcharts={Highcharts}
        options={{
          navigation: {
            buttonOptions: {
              enabled: false,
            }
          },
          chart: {
            type: 'pie',
            height: height,
            spacingBottom: legendHeight + 10,
            spacingLeft: 0,
            spacingRight: 0,
            marginRight: 0,
          },
          legend: {
            enabled: true,
            itemStyle: {
              fontWeight: 'normal',
            },
            // floating: true,
            align: 'left',
            verticalAlign: 'middle',
            layout: 'vertical',
            itemDistance: 3,
            itemMarginBottom: 10,
            labelFormatter: function () {
              // return 0;
              return '<b>' + valueFormatter({value: this.y}) + '%</b> ' + this.name.toLowerCase();//{value}<br/>{name}BINGO'
            },
            // maxHeight: legendHeight,
            // y: legendHeight + 20,
          },
          yAxis: {
            labels: {
              format: '{value}%',
              allowOverlap: false,
            },
            title: '',
            max: 100,
            reversedStacks: false,
          },
          plotOptions: {
            // series: {
            //   stacking: 'normal',
            // },
            pie: {
              showInLegend: true,
              dataLabels: {
                enabled: false,
                formatter: function () {
                  const self: any = this;
                  const value = valueFormatter({ value: self.y });
                  return `${value}%<br /><b>${self.point.name}</b>`;
                },
                crop: true,
                overflow: 'justify',
                useHTML: true,
              },
              minSize: width ? width * 0.4 : undefined,
              center: [null, '50%'],
              // minSize: containerRef.current?.offsetWidth * 0.33 || undefined,
            },
          },
          tooltip: {
            // enabled: false,
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
              // const max = this.series.yAxis.max;
              const value = this.y;
              let ret = `${
                this.key
              }: </b><b>${valueFormatter({ value })}%`;
              return ret;
            },
          },
          title: {
            text: null,
          },
          credits: {
            enabled: false,
          },
          responsive: {
            rules: [
              {
                condition: {
                  maxWidth: 200,
                },
                chartOptions: {
                  chart: {
                    height: '110%',
                  }
                }
              },
              {
                condition: {
                  maxWidth: 300,
                },
                chartOptions: {
                  legend: {
                    align: 'middle',
                    verticalAlign: 'bottom',
                    // layout: 'horizontal',
                    y: 0,
                    itemMarginBottom: 5,
                  },
                  chart: {
                    height: '100%',
                    spacingBottom: 0,
                  },
                  plotOptions: {
                    pie: {
                      center: [null, '25%'],
                      size: '65%',
                    }
                  }
                },
              },
            ]
          },
          series: [
            // this series for pie chart
            {
              name: 'Fractions of generation',
              data: [

                {
                  name: 'To demand directly',
                  y: roundToHundredth(analysisResult.f_DD * 100),
                  color: colors.green,
                },
                {
                  name: 'To demand via storage',
                  y: roundToHundredth(analysisResult.f_DVS * 100),
                  color: colors.yellow,
                },
                {
                  name: 'Lost in storage',
                  y: roundToHundredth(analysisResult.f_LIS * 100),
                  color: colors.gray,
                },
                {
                  name: 'Curtailed',
                  y: roundToHundredth(analysisResult.f_curtail * 100),
                  color: colors.black,
                }
              ]
            },
            // these series for bar chart
            // {
            //   name: 'To demand directly',
            //   color: colors.green,
            //   data: [roundToHundredth(analysisResult.f_DD * 100)]
            // },
            // {
            //   name: 'To demand via storage',
            //   color: colors.yellow,
            //   data: [roundToHundredth(analysisResult.f_DVS * 100)]
            // },
            // {
            //   name: 'Lost in storage',
            //   color: colors.gray,
            //   data: [roundToHundredth(analysisResult.f_LIS * 100)]
            // },
            // {
            //   name: 'Curtailed',
            //   color: colors.black,
            //   data: [roundToHundredth(analysisResult.f_curtail * 100)]
            // }
          ],
        }}
      />

    </div>
  )
}

const StorageTable = ({
  storageSizeUnit,
  setStorageSizeUnit,
  demandSize,
  demandSizeUnit,
  demandValueMultiplier,
  shouldDisplayStorageSizesAsAbsolute,
  analysisResult,
}: {
  storageSizeUnit: string,
  setStorageSizeUnit: React.Dispatch<React.SetStateAction<'relative' | 'absolute'>>,
  demandSize: string,
  demandSizeUnit: string,
  demandValueMultiplier: number,
  shouldDisplayStorageSizesAsAbsolute: boolean,
  analysisResult: any,
}) => {

  const { isComparisonMode } = React.useContext(ModuleStateContext);

  return (
    <>
      {!isComparisonMode &&
        <div className="flex items-center mt-1 mb-3">
          <div className="text-lg font-bold text-gray-700 flex-shrink-0 mr-4">Storage size</div>
          <Styles.Select
            onClick={(e) => {
              e.stopPropagation(); // prevent toggling accordion
            }}
            onChange={(e) => {
              const newStorageSizeUnit = e.target.value as 'relative' | 'absolute';
              setStorageSizeUnit(newStorageSizeUnit);
            }}
            defaultValue={storageSizeUnit}
            className="w-auto"
          >
            <option value="relative" label="(% of average demand)" />
            {demandSize &&
              <option value="absolute" label="(absolute)" />
            }
          </Styles.Select>
        </div>
      }
      <table className="table-auto w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left">Quantity</th>
            <th className="text-left pr-4">Value</th>
            <th className="text-left">Unit</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Energy capacity</td>
            <td>{valueFormatter({ value: roundToHundredth(analysisResult.EC * demandValueMultiplier) })}</td>
            <td>{shouldDisplayStorageSizesAsAbsolute  ? `${demandSizeUnit}h` : 'Hours of average demand'}</td>
          </tr>
          <tr>
            <td>Duration</td>
            <td>{valueFormatter({ value: roundToHundredth(analysisResult.d) })}</td>
            <td>Hours to empty from full, at max discharge</td>
          </tr>
          <tr>
            <td>Discharge power capacity</td>
            <td>{valueFormatter({ value: roundToHundredth(analysisResult.DPC * demandValueMultiplier) })}</td>
            <td>{shouldDisplayStorageSizesAsAbsolute ? demandSizeUnit : 'X average power demand'}</td>
          </tr>
          <tr>
            <td>Charge power capacity</td>
            <td>{valueFormatter({ value: roundToHundredth(analysisResult.CPC * demandValueMultiplier) })}</td>
            <td>{shouldDisplayStorageSizesAsAbsolute ? demandSizeUnit : 'X average power demand'}</td>
          </tr>
        </tbody>
      </table>
    </>
  )
}

const periods: Record<string, number> = {
  "day": 24,
  "week": 168,
  "month": 730,
  "quarter": 2190,
  "year": 8760,
};

const timeStepOptions = ['hour', 'day', 'week', 'month', 'quarter', 'year']

const timeStepTransformData = (timeStep: string, data: number[][] | Array<Array<number | number[]>>) => {
  if (timeStep === 'hour') {
    return data
  }
  const dataLength = data.length
  if (!dataLength) {
    return data
  }
  const timeSteppedData = []
  const numCols = data[0].length - 1
  let timeStepMultiplier = periods[timeStep]
  const numChunks = Math.floor(dataLength / timeStepMultiplier)
  // console.log('numChunks: ', numChunks)
  for (let step = 0; step < numChunks; step++) {
    const dataStartIndexForChunk = step * timeStepMultiplier
    // sum each data column
    const chunkData = [step + 1] // 1-index the x values, not 0-index, for user-friendliness; this first element is the x-axis value
    for (let col = 1; col <= numCols; col++) {
      const chunkSum = sumArray(
        data.slice(
          dataStartIndexForChunk,
          dataStartIndexForChunk + timeStepMultiplier
        ).map(dataTuplet => {
          return typeof dataTuplet[col] === 'object' ? dataTuplet[col][0] : dataTuplet[col]
        })
      )
      chunkData.push(chunkSum / timeStepMultiplier)
    }
    timeSteppedData.push(chunkData)
  }
  return timeSteppedData;
}

type PowerGreenfieldChartControlHandler = {
  startDay: number;
  setStartDay: React.Dispatch<React.SetStateAction<number>>;
  timePeriod: string;
  setTimePeriod: React.Dispatch<React.SetStateAction<string>>;
  timeStep: string;
  setTimeStep: React.Dispatch<React.SetStateAction<string>>;
}

const xAxisTickIntervalsWithPeriodAndTimeStep = {
  day: {
    hour: 6
  },
  week: {
    hour: 24,
    day: 1,
  },
  month: {
    hour: 168,
    day: 7,
    week: 1,
  },
  quarter: {
    hour: 730,
    day: 30,
    week: 1,
    month: 1,
  },
  year: {
    hour: 2190,
    day: 90,
    week: 10,
    quarter: 1,
  }
}

const Figures = ({
  demandSize,
}: {
  demandSize: string,
}) => {
  // const pieChartContainerWidth = useWidth(containerRef);
  // useChartResizing(chartRef, containerRef);

  const { demandSizeUnit, demandSizeValue } = parseDemandSize(demandSize);
  const [storageSizeUnit, setStorageSizeUnit ] = React.useState<'relative' | 'absolute'>('relative')
  const shouldDisplayStorageSizesAsAbsolute = !!demandSize && storageSizeUnit === 'absolute';
  const demandValueMultiplier = shouldDisplayStorageSizesAsAbsolute ? demandSizeValue : 1;

  const rowContainerRef = React.useRef();
  const overallFigureRowWidth = useWidth(rowContainerRef);

  const chartControlHandlers = Array(maxComparisonResultCols).fill(null).map((o, i) => {
    const [startDay, setStartDay] = useState(0);
    const [timePeriod, setTimePeriod] = useState('week');
    const [timeStep, setTimeStep] = React.useState('hour');
    return {
      startDay, setStartDay,
      timePeriod, setTimePeriod,
      timeStep, setTimeStep,
    }
  }) as PowerGreenfieldChartControlHandler[];

  const { comparisonCases, isComparisonMode, chartControlAllocation } = React.useContext(ModuleStateContext);

  const chartRefs = Array(maxComparisonResultCols).fill(null).map(o => {
    return React.useRef(null);
  });
  // const containerRef = React.useRef(null);
  const containerRefs = Array(maxComparisonResultCols).fill(null).map(o => {
    return React.useRef(null);
  })
  // chartRefs.map((chartRef, comparisonIndex) => {
  //   useChartResizing({
  //     chartRef,
  //     containerRef: containerRefs[comparisonIndex],
  //     deps: [comparisonCases?.map(comparisonCase => comparisonCase.id)],
  //     height: 120,
  //   });
  // })

  const analysisResults = comparisonCases?.map(comparisonCase => {
    if (!comparisonCase.data?.analysisResult) {
      return null;
    }
    return {
      ...comparisonCase.data?.analysisResult,
      id: comparisonCase.id
    }
  });

  if (analysisResults?.every(analysisResult => !analysisResult)) {
    return null;
  }

  const arrayOfChartsData = analysisResults?.map((analysisResult, comparisonIndex) => {

    // console.log('inside one arrayOfChartsData');

    if (!analysisResult) return null;

    const { startDay, timePeriod, timeStep } =
      chartControlAllocation === 'group' ?
      chartControlHandlers[0]
      :
      chartControlHandlers[comparisonIndex]
    ;

    const startHour = startDay * 24;
    const numHours = periods[timePeriod];

    const analysisData = (values: number[]) => {
      const data: number[][] = [];

      for (let x = 0; x < numHours; x++) {
        const hour = x + startHour;
        const i = hour % periods["year"];
        data.push([x + 1, values[i]]); // 1-index the x axis values for user friendliness
      }

      return timeStepTransformData(timeStep, data);
    };

    let generationToData = [];
    let generationFromData = [];
    let demandFromData = [];
  
    for (let x = 0; x < numHours; x++) {
      
      const hour = x + startHour;
      const i = hour % periods["year"];

      generationToData.push([
        x + 1, // 1-index the x-axis, not 0-index, for user friendliness
        analysisResult?.G_curtailed[i] || 0,
        analysisResult?.G_storage[i] || 0,
        analysisResult?.G_demand[i] || 0,
      ]);

      generationFromData.push([
        x + 1,
        analysisResult?.G_ng[i] || 0,
        analysisResult?.G_wind[i] || 0,
        analysisResult?.G_solar[i] || 0,
        analysisResult?.G_nuclear[i] || 0,
      ]);

      demandFromData.push([
        x + 1,
        analysisResult?.D_storage[i] || 0,
        // analysisResult?.D_gen[i] || 0,
        analysisResult?.G_ng[i] || 0,
        analysisResult?.G_SW_2_D[i] || 0,
      ]);
    }

    generationToData = timeStepTransformData(timeStep, generationToData)
    generationFromData = timeStepTransformData(timeStep, generationFromData)
    demandFromData = timeStepTransformData(timeStep, demandFromData)

    const steps: Record<string, number> = {
      "hour": 1,
      "day": 24,
      "week": 168,
      "month": 730,
      "quarter": 2190,
      "year": 8760,
    };
    const stepValuesAsArray = Object.keys(steps).map(key => steps[key]);

    const stepIndexOfPeriod = stepValuesAsArray.indexOf(steps[timePeriod])
    const stepsPerPeriod = stepValuesAsArray[stepIndexOfPeriod] / steps[timeStep];

    const stepsPerPeriodOneBelowPeriod = stepValuesAsArray[stepIndexOfPeriod - 1] / steps[timeStep];

    // switch to bar chart when we have less than 24 x-axis data points
    const chartType = generationToData.length < 24 ? 'column' : 'area';

    // calculate intuitive x-axis tick/label positions based on lookup table, depending on timePeriod and timeStep
    const xAxisTickInterval = xAxisTickIntervalsWithPeriodAndTimeStep[timePeriod]?.[timeStep] || 1;
    const numXAxisTicks = Math.floor(stepsPerPeriod / xAxisTickInterval);
    const xAxisTickPositions = new Array(numXAxisTicks || 0).fill(0).map((o, index) => (index + 1) * xAxisTickInterval - 1);
  
    const chartOptions = {//merge(defaultChartOptions([]), {
      chart: {
        zoomType: 'x',
        height: '48%',
        spacingBottom: 43,
      },
      xAxis: {
        labels: {
          step: 0,
          // allowOverlap: true,
        },
        tickPositions: xAxisTickPositions,
        title: {
          enabled: true,
          text: `${timeStep} of ${timePeriod}`,
        },
        plotLines: [
          {
            value: periods["year"] - startHour,
            label: {
              text: "Wrapped",
              style: {
                color: "black",
                transform: "translate(6px, 10px)",
                fontWeight: "bold",
              },
            }
          }
        ],
      },
      plotOptions: {
        area: {
          turboThreshold: 10000,
        },
        line: {
          turboThreshold: 10000,
        },
      },
      legend: {
        floating: true,
        maxHeight: 43,
        y: 43,
        x: 0,
        layout: 'horizontal',
        verticalAlign: 'bottom',
      },
      tooltip: {
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
      responsive: undefined,
    }

    if (!(startHour + numHours > periods["year"])) {
      // not wrapped
      chartOptions.xAxis.plotLines = [];
    }

    let areaDatasets: Dataset[] = [];
    let lineDatasets: Dataset[] = [];

    if (analysisResult) {
      areaDatasets = [
        {
          label: "Generation to",
          columns: ["Hour", "Curtailment", "Storage", "Demand"],
          data: generationToData,
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Generation from",
          columns: ["Hour", "Natural gas", "Wind", "Solar", "Nuclear"],
          data: generationFromData,
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Demand from",
          columns: ["Hour", "Storage", "Natural gas", "Solar wind nuclear"],
          data: demandFromData,
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Demand",
          columns: ["Hour", "Demand"],
          data: analysisData(analysisResult.D),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Generation",
          columns: ["Hour", "Generation"],
          data: analysisData(analysisResult.G),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Generation - demand",
          columns: ["Hour", "Generation - deman"],
          data: analysisData(analysisResult.G_minus_D),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Solar generation",
          columns: ["Hour", "Solar generation"],
          data: analysisData(analysisResult.G_solar),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Wind generation",
          columns: ["Hour", "Wind generation"],
          data: analysisData(analysisResult.G_wind),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Natural gas generation",
          columns: ["Hour", "Natural gas generation"],
          data: analysisData(analysisResult.G_ng),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Nuclear generation",
          columns: ["Hour", "Nuclear generation"],
          data: analysisData(analysisResult.G_nuclear),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Storage power",
          columns: ["Hour", "Storage power"],
          data: analysisData(analysisResult.P_storage),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Storage energy",
          columns: ["Hour", "Storage energy"],
          data: analysisData(analysisResult.E_storage),
          axis: 1,
          unit: "hours of average demand",
        },
      ];

      lineDatasets = [
        {
          label: "Demand",
          columns: ["Hour", "Demand"],
          data: analysisData(analysisResult.D),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Generation",
          columns: ["Hour", "Generation"],
          data: analysisData(analysisResult.G),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Generation - demand",
          columns: ["Hour", "Generation - demand"],
          data: analysisData(analysisResult.G_minus_D),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Solar generation",
          columns: ["Hour", "Solar generation"],
          data: analysisData(analysisResult.G_solar),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Wind generation",
          columns: ["Hour", "Wind generation"],
          data: analysisData(analysisResult.G_wind),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Natural gas generation",
          columns: ["Hour", "Natural gas generation"],
          data: analysisData(analysisResult.G_ng),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Nuclear generation",
          columns: ["Hour", "Nuclear generation"],
          data: analysisData(analysisResult.G_nuclear),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Storage power",
          columns: ["Hour", "Storage power"],
          data: analysisData(analysisResult.P_storage),
          axis: 0,
          unit: "% of average demand",
        },
        {
          label: "Storage energy",
          columns: ["Hour", "Storage energy"],
          data: analysisData(analysisResult.E_storage),
          axis: 0,
          unit: "hours of average demand",
        },


        {
          label: "Demand",
          columns: ["Hour", "Demand"],
          data: analysisData(analysisResult.D),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Generation",
          columns: ["Hour", "Generation"],
          data: analysisData(analysisResult.G),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Generation - demand",
          columns: ["Hour", "Generation - deman"],
          data: analysisData(analysisResult.G_minus_D),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Solar generation",
          columns: ["Hour", "Solar generation"],
          data: analysisData(analysisResult.G_solar),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Wind generation",
          columns: ["Hour", "Wind generation"],
          data: analysisData(analysisResult.G_wind),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Natural gas generation",
          columns: ["Hour", "Natural gas generation"],
          data: analysisData(analysisResult.G_ng),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Nuclear generation",
          columns: ["Hour", "Nuclear generation"],
          data: analysisData(analysisResult.G_nuclear),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Storage power",
          columns: ["Hour", "Storage power"],
          data: analysisData(analysisResult.P_storage),
          axis: 1,
          unit: "% of average demand",
        },
        {
          label: "Storage energy",
          columns: ["Hour", "Storage energy"],
          data: analysisData(analysisResult.E_storage),
          axis: 1,
          unit: "hours of average demand",
        },
      ];
    }

    // add scalar values + unit labels to each dataset
    areaDatasets.forEach((dataset, index) => {
      if (dataset.label === 'Storage energy') {
        areaDatasets[index].scalarUnit = `${demandSizeUnit}h`;
      } else {
        areaDatasets[index].scalarUnit = demandSizeUnit;
      }
      areaDatasets[index].scalar = demandSizeValue;
      // areaDatasets[index].stacking = chartType === 'bar' ? 'normal' : undefined; // show stacked bar charts if less than 24 x-axis data points
    })
    lineDatasets.forEach((dataset, index) => {
      if (dataset.label === 'Storage energy' && demandSize) {
        lineDatasets[index].scalarUnit = `${demandSizeUnit}h`;
      } else {
        lineDatasets[index].scalarUnit = demandSizeUnit;
      }
      lineDatasets[index].scalar = demandSizeValue;
    })

    return {
      chartOptions,
      areaDatasets,
      lineDatasets,
      chartType,
    }
  })

  // const prototypeCaseChartOptions = arrayOfChartsData?.find(o => !!o)?.chartOptions;
  const chartOptionsByCase = arrayOfChartsData?.map(o => o?.chartOptions);

  return (
    <>

      <PowerGreenfieldBarFigs />

      {/* <Accordion
        title="Generation"
        defaultOpen={true}
        stickyHeader={true}
      >
        <ComparisonRow
          sidebar={<></>}
          content={analysisResults?.map((analysisResult, comparisonIndex) => {
            // const containerRef = containerRefs[comparisonIndex];
            // const chartRef = chartRefs[comparisonIndex];

            if (!analysisResult) {
              return <div key={comparisonIndex}></div>;
            }

            return (
              <div key={comparisonIndex}>
                <GenerationChart comparisonIndex={comparisonIndex} demandSize={demandSize} />
              </div>
            )
          })}
        />
        <hr />
      </Accordion> */}
      <Accordion
        title="Equipment size"
        defaultOpen={true}
        stickyHeader={true}
      >
        <ComparisonRow
          sidebar={
            <div className="pt-3">
              <Styles.Label className="mb-2 !font-bold">Storage size</Styles.Label>
              <Styles.Select
                onClick={(e) => {
                  e.stopPropagation(); // prevent toggling accordion
                }}
                onChange={(e) => {
                  const newStorageSizeUnit = e.target.value as 'relative' | 'absolute';
                  setStorageSizeUnit(newStorageSizeUnit);
                }}
                defaultValue={storageSizeUnit}
                className="w-auto"
              >
                <option value="relative" label="(% of average demand)" />
                {demandSize &&
                  <option value="absolute" label="(absolute)" />
                }
              </Styles.Select>
            </div>
          }
          content={analysisResults?.map((analysisResult, comparisonIndex) => {
            // const containerRef = containerRefs[comparisonIndex];
            // const chartRef = chartRefs[comparisonIndex];
            if (!analysisResult) {
              return <div key={comparisonIndex}></div>;
            }
            return (
              <div key={comparisonIndex} className="pt-2 pb-5">
                <StorageTable
                  analysisResult={analysisResult}
                  // comparisonIndex={comparisonIndex}
                  demandSize={demandSize}
                  demandSizeUnit={demandSizeUnit}
                  demandValueMultiplier={demandValueMultiplier}
                  storageSizeUnit={storageSizeUnit}
                  setStorageSizeUnit={setStorageSizeUnit}
                  shouldDisplayStorageSizesAsAbsolute={shouldDisplayStorageSizesAsAbsolute}
                />
              </div>
            )
          })}
        />
      </Accordion>

      


      <Accordion
        title={(() => {
          return (
            <div className="flex items-center">
              Over Time
            </div>
          )
        })()}
        defaultOpen={true}
        stickyHeader={true}
        stickyIndex={0}
        padContentTop={false}
        headerClassName="h-12" //mt-[-1.5px]
        titleClassName={`mr-3 pr-3 ${!isComparisonMode ? 'border-r border-gray-300' : ''}`}
        headerLayout="comparisonRow"
        headerContentWhenOpen={
          chartControlAllocation === 'individual'
          ?
          analysisResults?.map((analysisResult, comparisonIndex) => {
            return <HourlyFigureControls key={comparisonIndex} chartControlHandler={chartControlHandlers[comparisonIndex]} />
          })
          :
          <div style={{gridColumn: "span " + (comparisonCases?.length ?? 0) + 1}}>
            <HourlyFigureControls chartControlHandler={chartControlHandlers[0]} />
          </div>
        }
      >

        <div className={`divide-y ${isComparisonMode ? '' : 'comparison-cell'}`}>
          <MultiDatasetFigure
            datasetsByCase={arrayOfChartsData?.map(data => data?.areaDatasets)}
            isYears={false}
            chartOptionsByCase={chartOptionsByCase}
            colors={areaChartColors}
            scaleAxes={true}
            defaultPrimaryOutput={'generation from'} // Generation from
            primaryChartTypes={arrayOfChartsData?.map(o => o?.chartType)}
          />
          <MultiDatasetFigure
            datasetsByCase={arrayOfChartsData?.map(data => data?.areaDatasets)}
            isYears={false}
            chartOptionsByCase={chartOptionsByCase}
            colors={areaChartColors}
            scaleAxes={true}
            defaultPrimaryOutput="generation to" // Generation to
            primaryChartTypes={arrayOfChartsData?.map(o => o?.chartType)}
            />
          <MultiDatasetFigure
            datasetsByCase={arrayOfChartsData?.map(data => data?.areaDatasets)}
            isYears={false}
            chartOptionsByCase={chartOptionsByCase}
            colors={areaChartColors}
            scaleAxes={true}
            defaultPrimaryOutput="demand from" // Demand from
            primaryChartTypes={arrayOfChartsData?.map(o => o?.chartType)}
            />

          <MultiDatasetFigure
            datasetsByCase={arrayOfChartsData?.map(data => data?.lineDatasets)}
            isYears={false}
            chartOptionsByCase={chartOptionsByCase}
            colors={lineChartColors}
            showInLegend={lineChartLegend}
            scaleAxes={true}
            primaryChartType="line"
            defaultPrimaryOutput="generation - demand" // Generation - demand
            defaultSecondaryOutput="storage power"
            primaryChartTypes={comparisonCases?.map(o => 'line')}
          />
          <MultiDatasetFigure
            datasetsByCase={arrayOfChartsData?.map(data => data?.lineDatasets)}
            isYears={false}
            chartOptionsByCase={chartOptionsByCase}
            colors={lineChartColors}
            showInLegend={lineChartLegend}
            scaleAxes={true}
            primaryChartType="line"
            defaultPrimaryOutput="storage energy" // Storage energy
            primaryChartTypes={comparisonCases?.map(o => 'line')}
            />
        </div>
      </Accordion>
    </>
  );
}
