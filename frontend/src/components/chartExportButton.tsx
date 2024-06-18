import * as React from "react"
import { Menu, Transition } from '@headlessui/react'
import Highcharts from "highcharts";
import HighchartsExporting from 'highcharts/modules/exporting';
import HighchartsOfflineExporting from 'highcharts/modules/offline-exporting';
import HighchartsExportData from 'highcharts/modules/export-data';
import { isBrowser, getHeaderTitle } from "../utils";

// Highcharts modules are required for exporting
// ...and are browser-only libs, so they will break the build
// if called on the server
if (isBrowser()) {
  HighchartsExporting(Highcharts);
  HighchartsOfflineExporting(Highcharts);
  HighchartsExportData(Highcharts);
}

const menuGroups = [
  [
    {
      label: 'SVG',
      fileType: 'image/svg+xml',
    },
    {
      label: 'PNG',
      fileType: 'image/png',
    },
    {
      label: 'JPEG',
      fileType: 'image/jpeg',
    },
  ],
  [
    {
      label: 'CSV',
      fileType: 'text/csv'
    },
  ]
]

export type DownloadChartAsTypeProps = {
  type: string;
  chartRef: React.MutableRefObject<any>;
  chartTitle: string;
}

const downloadChartAsType = async ({
  type,
  chartRef,
  chartTitle,
}: DownloadChartAsTypeProps): Promise<void> => {
  const filename = ['sesame', getHeaderTitle(), chartTitle].join('_');
  if (type === 'text/csv') {
    chartRef.current?.chart.downloadCSV({filename: filename});
  } else {
    chartRef.current?.chart.exportChartLocal({type: type, filename: filename});
  }
}

export const ChartExportButton = ({
  chartTitle,
  chartRef,
  className = '',
}: {
  chartTitle: string;
  chartRef: React.MutableRefObject<any>;
  className?: string;
}) => {

  const [isExporting, setIsExporting] = React.useState(false);

  return (
    <div className={`absolute top-0 right-1 ${className}`}>
      <Menu as="div" className="z-[5] relative inline-block text-right">
        {({ open }) => (
          <>
            <div>
              <Menu.Button className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-2 py-2 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-indigo-500">
                {isExporting ?
                  <svg className="inline animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                :
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                }
              </Menu.Button>
            </div>
            <Transition
              show={open}
              as={React.Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items
                static
                className="origin-top-right absolute right-0 mt-2 w-16 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none"
              >
                {menuGroups.map((group, groupIndex) => {
                  return (
                    <div className="py-1" key={groupIndex}>
                      {group.map((item, itemIndex) => {
                        return (
                          <Menu.Item key={itemIndex}>
                            <a
                              href="#"
                              className="text-gray-800 block px-4 py-2 text-sm hover:bg-gray-100 hover:text-gray-900"
                              onClick={(e) => {
                                e.preventDefault();
                                setIsExporting(true);
                                downloadChartAsType({type: item.fileType, chartTitle: chartTitle.replace(/ /gi, '_'), chartRef: chartRef}).then(() => {
                                  setIsExporting(false);
                                });
                              }}
                            >
                              {item.label}
                            </a>
                          </Menu.Item>
                        )
                      })}
                    </div>
                  )
                })}
              </Menu.Items>
            </Transition>
          </>
        )}
      </Menu>
    </div>
  )
}