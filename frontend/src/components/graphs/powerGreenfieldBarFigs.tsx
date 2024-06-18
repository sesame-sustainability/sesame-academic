import * as React from "react"
import Accordion from "../accordion"
import { getCaseNameFromComparisonCaseAtIndex, ModuleStateContext } from "../comparableResultsModule"
import { ReorderableChartGrid } from "../pages/LCATEA"
import { teaChartOptions } from "../pages/TEA"
import Highcharts, { Chart, merge } from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { ChartTitle, Select } from "../styles"
import { ChartExportButton } from "../chartExportButton"
import { Toggle } from "../toggle"
import { sumArray } from "../../utils"
import { useAtomValue } from "jotai"
import { parseDemandSize, powerGreenfieldDemandSizeAtom } from "../pages/pps"

type OutputMapping = {
  label: string
  dataMappings: Array<{label: string, key: string}>
  unit: string
  value?: string
  displayByDefault?: boolean
  showDemandSizeUnit?: boolean
  showRelativeUnit?: boolean
}

const outputMappings: OutputMapping[] = [
  {
    label: 'Generation from',
    displayByDefault: true,
    dataMappings: [
      {
        label: "Nuclear",
        key: "nuclear_gen_over_D",
      },
      {
        label: "Solar",
        key: "solar_gen_over_D",
      },
      {
        label: "Wind",
        key: "wind_gen_over_D",
      },
      {
        label: "Natural gas",
        key: "NG_gen_over_D",
      },
    ],
    unit: 'share',
    showDemandSizeUnit: true,
    showRelativeUnit: true,
  },
  {
    label: 'Generation to',
    displayByDefault: true,
    dataMappings: [
      {
        label: "Demand direct",
        key: "G_2_demand_over_D",
      },
      {
        label: "Demand via storage",
        key: "G_2_S_2_D_over_D",
      },
      {
        label: "Storage loss",
        key: "G_2_LIS_over_D",
      },
      {
        label: "TD loss",
        key: "G_2_TD_loss_over_D",
      },
      {
        label: "Curtail",
        key: "G_2_curt_over_D",
      },
    ],
    unit: 'share',
    showDemandSizeUnit: true,
    showRelativeUnit: true,
  },
  {
    label: 'Renewable generation to',
    dataMappings: [
      {
        label: "Demand direct",
        key: "f_ren_demand",
      },
      {
        label: "Demand via storage",
        key: "f_ren_storage",
      },
      {
        label: "Storage loss",
        key: "f_ren_LIS",
      },
      {
        label: "TD loss",
        key: "f_ren_TD_loss.",
      },
      {
        label: "Curtail",
        key: "f_ren_curt",
      },
    ],
    unit: 'share',
    showDemandSizeUnit: true,
    showRelativeUnit: true,
  },
  {
    label: 'GHG emissions by tech',
    displayByDefault: true,
    dataMappings: [
      {
        label: "Nuclear",
        key: "emissions_nuclear"
      },
      {
        label: "Solar",
        key: "emissions_solar"
      },
      {
        label: "Wind",
        key: "emissions_wind"
      },
      {
        label: "Natural gas",
        key: "emissions_ng"
      },
      {
        label: "Storage",
        key: "emissions_battery"
      },
    ],
    unit: 'gCO₂e/kWh',
  },
  {
    label: 'Costs by tech',
    displayByDefault: true,
    dataMappings: [
      {
        label: 'Nuclear',
        key: 'nuclear cost',
      },
      {
        label: 'Solar',
        key: 'solar cost',
      },
      {
        label: 'Wind',
        key: 'wind cost',
      },
      {
        label: 'Natural gas',
        key: 'ng cost',
      },
      {
        label: 'Storage',
        key: 'battery cost',
      }
    ],
    unit: '$/MWh',
    value: 'Cost',
  },
  {
    label: 'Costs by type',
    dataMappings: [
      {
        label: "Capital",
        key: "CAPEX",
      },
      {
        label: "Fixed",
        key: "FOM",
      },
      {
        label: "Fuel",
        key: "fuel",
      },
      {
        label: "Non-fuel variable",
        key: "VOM",
      },
      {
        label: "Delivery",
        key: "delivery",
      },
      {
        label: "Tax",
        key: "tax",
      },
    ],
    unit: '$/MWh',
    value: 'Cost',
  },
]

export const PowerGreenfieldBarFigs = () => {

  const defaultOutputMappings = outputMappings.filter(mapping => mapping.displayByDefault);

  return (
    <Accordion
      title="Summary"
      defaultOpen={true}
      stickyHeader={true}
      stickyIndex={0}
    >
      <ReorderableChartGrid
        oneColumnOrder={[0,1,2,3]}
        twoColumnOrder={[0,1,2,3]}
        blocks={
          defaultOutputMappings.map((outputMapping, index) => {
            const defaultOutputIndexOfThisFigure = outputMappings.indexOf(outputMapping);
            return (
              <BarFigure
                defaultOutputIndex={defaultOutputIndexOfThisFigure}
              />
            )
          })
        }
      />
    </Accordion>
  )
}

// type PowerGreenfieldBarFigUnit = 'relative' | 'share' | 'scaled'

const legendHeight = 50;

const powerGreenfieldBarFigOptions = {
  chart: {
    spacingBottom: legendHeight,
  },
  legend: {
    // floating: false,
    // labelFormatter: function() {
    //   if ()
    // },
    y: legendHeight,
  }
}


const BarFigure = ({
  defaultOutputIndex, 
}: {
  defaultOutputIndex: number,
}) => {

  const { comparisonCases } = React.useContext(ModuleStateContext)
  const comparisonCasesWithResults = comparisonCases?.filter(c => !!c?.data?.analysisResult)

  const [currentOutputIndex, setCurrentOutputIndex] = React.useState<number>(defaultOutputIndex)
  
  const outputMapping = outputMappings[currentOutputIndex]

  const [currentUnit, setCurrentUnit] = React.useState(outputMapping.unit)
  const [isChartStacked, setIsChartStacked] = React.useState(true)
  const chartRef = React.createRef<{ chart: Chart; container: React.RefObject<HTMLDivElement>; }>()


  const demandSize = useAtomValue(powerGreenfieldDemandSizeAtom)
  const { demandSizeValue, demandSizeUnit } = parseDemandSize(demandSize)
  
  // all PPS bar figs have a default unit from the backend, along with "share"
  const unitOptions = [outputMapping.unit]
  const necessaryUnits = ['share']
  necessaryUnits.forEach(unit => {
    if (!unitOptions.includes(unit)) {
      unitOptions.push(unit)
    }
  })
  if (outputMapping.showRelativeUnit) {
    unitOptions.push('relative')
  }
  if (demandSize && outputMapping.showDemandSizeUnit) {
    unitOptions.push('scaled')
  }

  const OutputChooser = React.memo(() => {
    return (
      <Select
        value={currentOutputIndex}
        onChange={(e) => setCurrentOutputIndex(parseInt(e.target.value))}
      >
        {outputMappings.map((outputMapping, index) => (
          <option value={index}>{outputMapping.label}</option>
        ))}
      </Select>
    )
  })

  const getUnitLabel = React.useCallback((unit: string) => {
    let label = ''
    if (unit === 'scaled') {
      if (demandSizeUnit) {
        if (demandSizeUnit === 'kW') {
          label = 'GWh'
        } else if (demandSizeUnit === 'GW') {
          label = 'TWh'
        }
      }
    } else if (unit === 'share') {
      label = 'share'
    } else if (unit === 'relative') {
      label = '% of demand'
    } else {
      label = unit
    }
    return label
  }, [demandSize, demandSizeUnit])

  const UnitChooser = () => {

    return (
      <Select
        value={currentUnit}
        onChange={(e) => setCurrentUnit(e.target.value)}
      >
        {unitOptions.map((unit, index) => {          
          return (
            <option value={unit}>({getUnitLabel(unit)})</option>
          )
        })}
      </Select>
    )
  }

  const transformData = React.useCallback((data: Array<object & { value: number }>) => {
    const barTotal = sumArray(data.map(d => d.value))
    let newData;
    if (currentUnit === 'share') {
      newData = data.map(bar => ({
        ...bar,
        value: bar.value / barTotal * 100,
      }))
    } else if (currentUnit === 'scaled') {
      newData = data.map(bar => ({
        ...bar,
        value: bar.value * demandSizeValue * 8760 / 1000
      }))
    } else if (currentUnit === 'relative') {
      newData = data.map(bar => ({
        ...bar,
        value: bar.value * 100
      }))
        
    } else {
      newData = data;
    }
    return newData;
  }, [currentUnit, unitOptions, demandSizeValue])

  const data = comparisonCasesWithResults?.map(comparisonCase => {
    const analysisResult = comparisonCase.data?.analysisResult;
    const dataMappings = outputMapping.dataMappings;
    return {
      columns: ['value', 'cost_category', 'cost_category_by_parts', 'pathway'],
      data: transformData(dataMappings.map(({label, key}) => ({
        value: analysisResult[key],
        cost_category: label,
        cost_category_by_parts: label,
        pathway: ''
      }))),
      title: comparisonCase.name || '',
      unit: getUnitLabel(currentUnit),
      value: outputMapping.value,
    }
  })

  const chartOptions = merge(
    teaChartOptions({
      teaData: data,
      categories: comparisonCasesWithResults?.map((comparisonCase, comparisonIndex) => comparisonCase.name ?? getCaseNameFromComparisonCaseAtIndex(comparisonCase, comparisonIndex)) ?? [],
      isChartStacked: isChartStacked,
    }),
    powerGreenfieldBarFigOptions
  )

  return (
    <div key={outputMapping.label} className="mt-3">
      <div className="grid grid-cols-2 gap-4">
        <OutputChooser />
        <UnitChooser />
      </div>
      <div className="relative pt-8 mt-4">
        <HighchartsReact
          ref={chartRef}
          highcharts={Highcharts}
          options={chartOptions}
        />,
        <div className="absolute top-0 left-0">
          <Toggle label="Stack Bars" value={isChartStacked} setValue={setIsChartStacked} />
        </div>
        <ChartExportButton chartRef={chartRef} chartTitle={outputMapping.label} />
      </div>
    </div>
  )

}