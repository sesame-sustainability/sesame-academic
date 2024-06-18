import { bodyFontFamily, CHART_ANIMATION_DURATION } from "../../utils/constants";
import { formatDecimal } from "../../utils";
import { chartColors, valueFormatter } from "../figures";

const buildSharedConfig = ({
  title,
  base,
  data,
  type = "emissions",
}: {
  title: string;
  base: number;
  data: {
    category: string;
    min: number;
    max: number;
    minPerc: number;
    maxPerc: number;
    default: string;
    minimizing: string;
    maximizing: string;
    unit?: string;
    data_lacking?: boolean;
  }[];
  type: string;
}) => {

  const legendHeightGuess = 50;
  const spacingBottom = 40;
  let min = 0;
  let max = 0;

  const sorted = data.map((item) => {
    item.minPerc = (item.min - base) / base * 100;
    item.maxPerc = (item.max - base) / base * 100;

    if (item.minPerc < min) {
      min = item.minPerc;
    }
    if (item.maxPerc > max) {
      max = item.maxPerc;
    }

    return item;
  }).sort((a, b) => {
    const spreadA = a.max - a.min;
    const spreadB = b.max - b.min;
    return spreadB - spreadA;
  });

  const dataLabel = (val: string | number | undefined) => {
    if (val === undefined) {
      return '';
    }

    if (typeof(val) !== 'string') {
      val = formatDecimal(val);
    }

    if (typeof(val) === 'string' && val.length > 20) {
      val = val.substring(0, 20) + '...';
    }
  
    return val;
  };

  const percPlotLine = (perc: number, align: string = 'center') => {
    return {
      value: perc,
      label: {
        text: formatDecimal(perc / 100 * base + base),
        verticalAlign: 'bottom',
        rotation: 0,
        align,
        y: 20,
        x: 0,
        style: {
          color: '#f00',
        },
      },
    }
  };
  
  return {
    chart: {
      type: "bar",
      height: data?.length * 30 + legendHeightGuess + spacingBottom,
      style: {
        fontFamily: bodyFontFamily.join(", "),
      },
      animation: {duration: CHART_ANIMATION_DURATION},
      spacingBottom: spacingBottom,
    },
    title: `${title}: Sensitivity`,
    navigation: {
      buttonOptions: {
        enabled: false,
      },
    },
    credits: {
      enabled: false,
    },
    yAxis: [
      {
        title: {
          text: null,
        },
        min: Math.min(min, -100),
        max: Math.max(max, 100),
        labels: {
          formatter: function () {
            return `${this.value}%`
          },
        },
        opposite: true,
        plotLines: [
          percPlotLine(-100),
          percPlotLine(-50),
          {
            value: 0,
            color: '#f00',
            zIndex: 5,
            label: {
              text: formatDecimal(base),
              verticalAlign: 'bottom',
              rotation: 0,
              align: 'center',
              y: 20,
              style: {
                color: '#f00',
                fontWeight: 'bold',
              },
            }
          },
          percPlotLine(50),
          percPlotLine(100, 'right'),
        ]
      },
      {
        title: {
          text: null,
          y: 30,
          style: {
            color: '#f00',
          }
        },
      }
    ],
    xAxis: {
      categories: sorted.map(({ category }) => category),
      labels: {
        formatter: function(): unknown {
          const item = data.find(({ category }) => category === this.value);
          if (!item) {
            return '';
          }
          let val = item.category;
          if (item.unit) {
            val += ` (${item.unit})`;
          }
          if (item.data_lacking) {
            val = `<span>${flagIconHtml}${val}</span>`;
          }
          return val;
        },
        style: {
          textAlign: 'right',
          textOverflow: undefined,
          zIndex: 0,
        },
        zIndex: 0,
        align: 'right',
        useHTML: true,
      },
    },
    series: [
      {
        threshold: 0,
        data: sorted.map(item => {
          if (item.minPerc === 0.0) {
            return null;
          } else {
            return item.minPerc;
          }
        }),
        color: chartColors.green,// "#7cb5ec",
        dataLabels: {
          formatter: function (): unknown {
            const item = data.find((item) => item.category === this.x);
            return dataLabel(item?.minimizing);
          },
          style: {
            color: '#666',
            fontWeight: 'normal',
          },
          // align: "left",
          position: 'left',
          inside: false,
          // x: -40,
        },
      },
      {
        threshold: 0,
        data: sorted.map(item => {
          if (item.maxPerc === 0.0) {
            return null;
          } else {
            return item.maxPerc;
          }
        }),
        color: chartColors.blue,//"#f7a35c",
        dataLabels: {
          formatter: function (): unknown {
            const item = data.find((item) => item.category === this.x);
            return dataLabel(item?.maximizing);
          },
          style: {
            color: '#666',
            fontWeight: 'normal',
          },
          // align: "right",
          position: 'right',
          inside: false,
          // x: 35,
        },
      },
    ],
    plotOptions: {
      series: { stacking: "normal" },
      bar: {
        dataLabels: {
          enabled: true,
        },
      },
    },
    legend: { enabled: false },
    tooltip: {
      backgroundColor: null,
      borderWidth: 0,
      shadow: false,
      useHTML: true,
      zIndex: 100,
      style: {
        zIndex: 100
      },
      formatter(): unknown {
        const item = data.find((item) => item.category === this.x);
        let change = null;
        let dir = null;

        if (this.y < 0) {
          change = item?.minimizing;
          dir = "decreases";
        } else if (this.y > 0) {
          change = item?.maximizing;
          dir = "increases";
        }

        const unit = item?.unit ? item.unit : '';

        const changeAsNumber = parseFloat(change ?? '')
        const isChangeANumber = Number.isFinite(changeAsNumber)
        if (isChangeANumber) {
          change = valueFormatter({value: changeAsNumber})
        }

        const dataLackingText = `<span style="flex items-center">${flagIconHtml} SESAME currently lacks data needed to estimate the 20th & 80th percentile values of this input. Instead, the input here is varied by plus and minus ${dataLackingPercentageVariation}% from its default value.</span>`

        const styles = `background: white; padding: 5px 8px; border-radius: 4px; border-width:1px; border-color: ${this.color}; color: #333;`

        return `<div class="shadow-lg" style="${styles}">${[
          `Changing <b>${this.x}</b>`,
          `from <b>${item?.default || 'default'}</b> to <b>${change}</b>${unit ? ` ${unit}` : ''}`,
          `${dir} ${type} by <b>${formatDecimal(Math.abs(this.y))}%</b>`// to <b>${formatDecimal(threshold * (1 + this.y/100))}</b>`
        ].join('<br>')}${item?.data_lacking ? `<br><br>${dataLackingText}` : ''}</div>`;
      },
    }
  }
};

export const tornadoChartOpts = (
  res: PathwayAnalysisResponse | undefined,
  type = "emissions",
) => {
  const data = res?.sensitivity?.inputs.map(input => {
    // console.log(input.data_lacking ? input.label : '')
    return {
      category: input.label,
      min: input.min_value,
      max: input.max_value,
      default: input.default_value,
      minimizing: input.minimizing_value,
      maximizing: input.maximizing_value,
      unit: input.unit,
      data_lacking: input.data_lacking,
    };
  });

  return {
    ...buildSharedConfig({
      base: res?.sensitivity?.base_value || 0,
      data: data || [],
      type,
    }),
  };
}

const flagIconHtml = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" style="display: inline;margin-right:5px; margin-top: -2px; transform: scale(0.75)" viewBox="0 0 20 20" fill="currentColor">
  <path fill-rule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clip-rule="evenodd" />
</svg>`

export const dataLackingPercentageVariation = 30