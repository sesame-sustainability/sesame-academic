import * as React from "react";
import useAppMetadata from "../../hooks/useAppMetadata";
import { capitalize } from "../../utils";
import { ModuleDispatchContext, ModuleStateContext } from "../comparableResultsModule";
import { chartColors } from "../figures";
import { MultiDatasetFigure, slugifyString } from "../graphs/multiDatasetFigure";
import { ComparisonInputHandler } from "../inputHandler";
import Layout from "../layout";
import SEO from "../seo";
import * as Styles from "../styles"

type ModuleInfo = {
  label: string,
  type: string,
  metadata: BasicModuleMetadata,
  apiPath: string,
};

const IndustryComponent = ({
  modules,
  chartType = 'column',
}: {
  modules: Record<string, ModuleInfo>;
  chartType?: string;
}) => {
  const { comparisonCases, subModuleType } = React.useContext(ModuleStateContext);
  const [moduleName, setModule] = React.useState<string>(Object.keys(modules)[0]);
  const dispatch = React.useContext(ModuleDispatchContext);

  const moduleInfo = React.useMemo(() => {
    return modules[moduleName];
  }, [moduleName]);

  React.useEffect(() => {
    dispatch({type: 'setSubModuleType', value: moduleInfo.type})
  }, [moduleInfo])
  
  // load Industry sub module type from saved case
  React.useEffect(() => {
    if (subModuleType) {
      setModule(subModuleType)
    }
  }, [subModuleType])

  const moduleSelector = (
    <div>
      <Styles.Select
        value={moduleName}
        onChange={e => {
          setModule(e.target.value);
          dispatch({type: 'resetComparisonCasesToOneEmptyCase'});
        }}
        id="select-industry-module"
      >
        {Object.keys(modules).map(moduleName => {
          const label = modules[moduleName].label;
          return (
            <option value={moduleName} label={label}></option>
          );
        })}
      </Styles.Select>
    </div>
  );

  return (
    <Layout
      secondCol={[<Figures chartType={chartType} moduleName={moduleName} />]}
      appHeaderContent={Object.keys(modules).length > 1 ? moduleSelector : <div></div>}
    >
      <ComparisonInputHandler
        moduleMetadata={moduleInfo.metadata}
        apiPathOverride={moduleInfo.apiPath}
      />
    </Layout>
  )
}

const Figures = ({chartType = 'column', moduleName = ''}) => {
  const { comparisonCases } = React.useContext(ModuleStateContext);
  const analysisResults = comparisonCases?.map(comparisonCase => {
    return comparisonCase?.data?.analysisResult;
  });

  const colorMapping = {} as Record<string, string>;

  const datasetsByCase = analysisResults?.map((analysisResult) => {
    if (analysisResult) {
      const years: number[] = analysisResult.years;
      return analysisResult.figures.map((figure) => {
        return {
          label: figure.label,
          unit: figure.unit,
          axis: figure.axis,
          columns: ['year'].concat(figure.datasets.map((dataset) => {
            if (dataset.color && dataset.color[0] === '#') {
              // already a HEX color
              colorMapping[dataset.label] = dataset.color;
            } else {
              colorMapping[dataset.label] = chartColors[dataset.color];
            }
            return dataset.label;
          })),
          data: years.map((year, yearIndex) => {
            return [year].concat(figure.datasets.map((dataset) => {
              let data = dataset.data;
              if (!data) {
                return null;
              }
              return data[yearIndex];
            }));
          }),
          seriesStyles: figure.datasets.reduce((res, dataset) => {
            res[dataset.label] = dataset.style;
            return res;
          }, {}),
        }
      });
    } else {
      return []
    }
  });

  // for calculating hacky x-axis min and max to get chart data to stretch to the fill the whole x-axis
  const prototypeAnalysisResult = analysisResults?.filter(a => !!a)?.[0];
  const numXAxisDataPoints = prototypeAnalysisResult?.years?.length;

  const numCharts = 3;
  type figType = object & {
    axis: number,
    label: string,
  }
  const defaultPrimaryChartOutputs: string[] = prototypeAnalysisResult?.figures
    ?.filter((fig: figType) => fig.axis === 0)
    .slice(0, numCharts)
    .map((fig: figType) => slugifyString(fig.label))

  return (
    <>
      {analysisResults?.some(analysisResult => !!analysisResult) &&
        <div className="divide-y">
          {defaultPrimaryChartOutputs.map((output, index) => (
            <MultiDatasetFigure
              key={index}
              defaultPrimaryOutput={output}
              datasetsByCase={datasetsByCase}
              colors={colorMapping}
              primaryChartTypes={comparisonCases?.map(c => chartType)}
              // primaryChartType={chartType}
              relativeYear={2020}
              chartOptionsByCase={comparisonCases?.map(c => ({
                xAxis: {
                  labels: {
                    step: 1,
                  },
                  min: chartType === 'area' ? 0.35 : undefined,
                  max: chartType === 'area' ? numXAxisDataPoints - 1.35 : undefined,
                },
                legend: {
                  floating: false,
                  // align: 'left',
                  // verticalAlign: 'middle',
                  maxHeight: 500,
                  // height: 130,
                  // layout: 'vertical',
                }
              }))}
              // order={seriesOrder}
              // colors={seriesColors}
              // display={display}
            />
          ))}
          {/* <FigureSet figureSet={figureSet} /> */}

        </div>

      }

    </>
  )
}

export const SingleIndustry = () => {
  const {
    industryCement: { industryCement: industryCementMetadata },
    industrySteel: { industrySteel: industrySteelMetadata },
    industryAluminum: { industryAluminum: industryAluminumMetadata },
  } = useAppMetadata();

  const cement: ModuleInfo = {
    label: 'Cement',
    type: 'cement',
    metadata: industryCementMetadata,
    apiPath: '/industry/cement',
    // endpoint: '/industry/cement/analysis',
  };

  const steel: ModuleInfo = {
    label: 'Iron and Steel',
    type: 'steel',
    metadata: industrySteelMetadata,
    apiPath: '/industry/steel',
    // endpoint: '/industry/steel/analysis',
  }

  const aluminum: ModuleInfo = {
    label: 'Aluminum',
    type: 'aluminum',
    metadata: industryAluminumMetadata,
    apiPath: '/industry/aluminum',
    // endpoint: '/industry/aluminum/analysis',
  }

  return <IndustryComponent
    modules={{
      'cement': cement,
      'steel': steel,
      'aluminum': aluminum,
    }}
  />;
};

export const IndustrialFleet = () => {
  const {
    industrialFleet: { industrialFleet: industrialFleetMetadata },
  } = useAppMetadata();

  const industrialFleet: ModuleInfo = {
    label: 'Industrial Fleet',
    type: 'industrial-fleet',
    metadata: industrialFleetMetadata,
    apiPath: '/industry/fleet',
    // endpoint: '/industry/fleet/analysis',
  };

  return <IndustryComponent
    modules={{
      'industrial-fleet': industrialFleet,
    }}
    chartType="area"
  />;
};