import React from "react";
import { Link } from "gatsby";
import differenceInDays from "date-fns/differenceInDays";

import { isBrowser, getChangeInDemandLast7Days } from "../utils";
import { balancingAreasDisplay } from "../utils/constants";

import SEO from "../components/seo";
import USDailyDemand from "../components/graphs/usDailyDemand";
import BADailyDemand from "../components/graphs/baDailyDemand";
import USAvgDailyDemand from "../components/graphs/usAvgDailyDemand";
import HourlyTotalsGraph from "../components/graphs/baHourlyTotals";
import { ChartWrapper, formatNegativePercent } from "../components/styles";
import {
  useDashboardData,
  usePeakEIASeries,
  useAvgTotalSeries,
} from "../hooks/useDashboardData";

const EiaPage = (): JSX.Element => {
  const { lastUpdated } = useDashboardData();
  const [baLoadProfileDelta, setBaLoadProfileDelta] = React.useState<
    Record<string, string>
  >({});
  const { year2020, allAveraged } = usePeakEIASeries();
  const avgTotalSeries = useAvgTotalSeries();

  const mostRecentAvg2020DataPoint: number[] = avgTotalSeries[0].data.pop() || [
    0,
  ];

  const onBAChange = React.useCallback(
    (delta: Record<string, string>) => setBaLoadProfileDelta(delta),
    []
  );

  return (
    <div className="bg-gray-100" style={{ borderTop: "1px solid #cbd5e0" }}>
      <div className="mx-auto max-w-screen-xl px-4 sm:px-6">
        <SEO title="COVID-19 Dashboard" />
        <div className="grid grid-cols-1">
          <div className="flex justify-between mt-10 mb-2">
            <h1 className="text-2xl font-semibold">COVID-19</h1>
            <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium leading-5 bg-blue-100 text-blue-800">
              <svg
                className="-ml-1 mr-1.5 h-2 w-2 text-blue-400"
                fill="currentColor"
                viewBox="0 0 8 8"
              >
                <circle cx="4" cy="4" r="3" />
              </svg>
              Last updated: {lastUpdated}
            </span>
          </div>
          <div className="col-span-1 bg-white p-6 shadow my-6">
            <p className="mb-6">
              <b>
                COVID-19 has dramatically changed the way we conduct our
                day-to-day lives.
              </b>{" "}
              The ripple effects are experienced in almost all sectors,
              including the energy sector. As part of our ongoing{" "}
              <Link to="/" className="text-blue-700 font-bold">
                SESAME tool
              </Link>{" "}
              development, researchers at MITEI will be highlighting these
              changes through various indicators on this dashboard. We are
              currently showcasing some of the trends in electricity.
            </p>
            <p className="font-bold">
              This dashboard is a work in progress, and will soon be expanded to
              include other energy sectors.{" "}
              <a
                href="https://mit.us4.list-manage.com/subscribe?u=1a57a715520513505ca5cda89&id=eb3c6d9c51&group[13581][8]=true"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-700"
              >
                Sign up to be notified of new releases ›
              </a>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1">
          <div className="col-span-1 bg-white p-6 shadow mb-6">
            <div className="grid lg:grid-cols-3 grid-cols-1 gap-6">
              <div className="text-center">
                <div className="max-w-xs m-auto">
                  Change in average U.S. electricity demand since March 16
                </div>
                <div>
                  {formatNegativePercent(
                    getChangeInDemandLast7Days(
                      avgTotalSeries[0].data,
                      avgTotalSeries[1].data,
                      -differenceInDays(
                        new Date(mostRecentAvg2020DataPoint[0]),
                        // if we want to include the 16th (Monday)
                        // we need to pass the 15th
                        new Date(2020, 2, 15)
                      )
                    )
                  )}
                </div>
              </div>
              <div className="text-center">
                <div className="max-w-xs m-auto">
                  Change in average total U.S. electricity demand in the last 7
                  days
                </div>
                <div className="mt-2">
                  {formatNegativePercent(
                    getChangeInDemandLast7Days(
                      avgTotalSeries[0].data,
                      avgTotalSeries[1].data,
                      -7
                    )
                  )}
                </div>
              </div>
              <div className="text-center">
                <div className="max-w-xs m-auto">
                  Change in peak U.S. electricity demand in the last 7 days
                </div>
                <div className="mt-2">
                  {formatNegativePercent(
                    getChangeInDemandLast7Days(
                      year2020.data,
                      allAveraged.data,
                      -7
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3 grid-cols-1 pb-6">
          <div className="lg:col-span-3 col-span-1">
            <USAvgDailyDemand />
          </div>
          <div className="grid gap-6 col-span-1 grid-rows-1 text-center">
            <div className="grid row-span-1 p-5 bg-white shadow">
              <div className="my-auto">
                <div className="text-md mb-6">
                  Hourly change in electricity demand:
                </div>
                <div className="grid grid-cols-2">
                  {Object.keys(baLoadProfileDelta).map((BA) => {
                    return (
                      <div key={BA} className="my-auto">
                        {formatNegativePercent(baLoadProfileDelta[BA])}

                        <div className="text-sm mb-4">
                          {`${
                            balancingAreasDisplay[BA as BalancingArea].long
                          } (${
                            balancingAreasDisplay[BA as BalancingArea].short
                          })`}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="text-xs">
                  Regions are approximated for presentation purposes and may not
                  represent exact geographic boundaries.
                </div>
              </div>
            </div>
          </div>
          <div className="lg:col-span-2 col-span-1">
            <ChartWrapper>
              {isBrowser() && <HourlyTotalsGraph onBAChange={onBAChange} />}
            </ChartWrapper>
          </div>
          <div className="lg:col-span-3 col-span-1">
            <ChartWrapper>{isBrowser() && <BADailyDemand />}</ChartWrapper>
            <ChartWrapper className="mt-6">
              {isBrowser() && <USDailyDemand />}
            </ChartWrapper>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EiaPage;
