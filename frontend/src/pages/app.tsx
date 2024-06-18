import React from "react";
import { Router, RouteComponentProps } from "@reach/router";
import { navigate } from "gatsby";
import PrivateRoute from "../components/privateRoute";
import { ComparableResultsModule } from "../components/comparableResultsModule";
import TEA from "../components/pages/TEA";
import { UnifiedLCATEA } from "../components/pages/LCATEA";
import Cars from "../components/pages/cars";
import PowerSystem from "../components/pages/powerSystem";
import PowerSystemHistorical from "../components/pages/powerSystemHistorical";
import LoginScreen from "../components/pages/login";
import PPS from "../components/pages/pps";
import { Dashboard } from "../components/pages/dashboard";
import { SingleIndustry, IndustrialFleet } from "../components/pages/industry";
import { UnderConstruction } from "../components/pages/underConstruction";
import { Settings } from "../components/pages/settings";
import { SavedCaseBrowser } from "../components/pages/savedCaseBrowser";
import { HelpPage } from "../components/pages/help";
import { QueryClient, QueryClientProvider } from "react-query";
import { UserProfile } from "../components/pages/userProfile";

const AppRedirect = () => {
  navigate('/app/dashboard');
  return null;
}

export const comparableResultsModules: ComparableResultsModuleProps[] = [
  {
    title: 'Cars',
    path: '/app/cars',
    type: 'fleet',
    group: 'systems',
    description: 'Analyze fleet lifecyle emissions',
    allowComparisons: true,
    allowCaseDuplication: true,
    showRunAllButton: true,
    allowChartTiling: true,
    apiPath: '/fleet',
    component: () => <Cars />
  },
  {
    title: 'Power',
    path: '/app/power',
    type: 'grid',
    group: 'systems',
    description: 'Analyze grid energy performance',
    allowComparisons: false,
    apiPath: '/grid',
    component: () => <PowerSystem />,
  },
  // {
  //   title: 'Power Historic',
  //   path: '/app/power-historic',
  //   type: 'powerHistoric',
  //   description: 'TBD',
  //   group: 'systems',
  //   component: () => <PowerSystemHistorical />,
  //   apiPath: '/system',
  //   allowComparisons: false,
  // },
  {
    title: 'Power Greenfield',
    path: '/app/power-greenfield',
    type: 'pps',
    group: 'systems',
    description: 'Drill down into grid emissions profiles and performance',
    allowComparisons: true,
    allowCaseDuplication: true,
    showRunAllButton: true,
    apiPath: '/pps',
    component: () => <PPS />
  },
  {
    title: 'Industrial Fleet',
    path: '/app/industrial-fleet',
    type: 'industrial-fleet',
    group: 'systems',
    description: 'Analyze hard-to-abate sector emissions',
    allowComparisons: true,
    allowCaseDuplication: true,
    showRunAllButton: true,
    apiPath: '/industry/fleet',
    component: () => <IndustrialFleet />,
  },
  {
    title: 'Build',
    buttonText: 'Paths',
    path: '/app/build',
    type: 'lca-tea',
    group: 'paths',
    description: 'Build and analyze a new pathway',
    allowComparisons: true,
    maxComparisonCases: 3,
    allowCaseDuplication: true,
    showRunAllButton: true,
    apiPath: '/lca',
    component: () => <UnifiedLCATEA />
  },
  {
    title: 'Costs',
    path: '/app/costs',
    type: 'tea',
    group: 'paths',
    description: 'Analyze costs of different pathways',
    apiPath: '/tea',
    component: () => <TEA />,
  },
  {
    title: 'Industry',
    path: '/app/industry',
    type: 'industry',
    group: 'paths',
    description: 'Cement, iron & steel, and aluminum manufacturing',
    allowComparisons: true,
    allowCaseDuplication: true,
    showRunAllButton: true,
    apiPath: '/industry/cement',
    component: () => <SingleIndustry />,
  },
];

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
})

const App = ({ location }: RouteComponentProps): JSX.Element => {

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <LoginScreen path="/app/login" />
        <PrivateRoute
          path="/app/dashboard"
          title="Dashboard"
          component={() => <Dashboard pathname={location?.pathname || ""} />}
        />
        <PrivateRoute
          path="/app"
          title="App"
          component={() => <AppRedirect />}
        />
        <PrivateRoute
          path="/app/profile"
          title="Profile"
          component={() => <UserProfile />}
        />
        <PrivateRoute
          path="/app/saved"
          title="Saved"
          component={() => <SavedCaseBrowser />}
        />
        <PrivateRoute
          path="/app/help"
          title="Help"
          component={() => <HelpPage />}
        />
        {comparableResultsModules.map(moduleData => (
          <PrivateRoute
            path={moduleData.path}
            key={moduleData.type}
            component={() => (
              <ComparableResultsModule moduleData={moduleData}>
                {moduleData.component()}
              </ComparableResultsModule>
            )}
          />
        ))}
        <PrivateRoute
          path="/app/settings"
          title="Settings"
          component={() => (
            <Settings title="Settings" />
          )}
        />
      </Router>
    </QueryClientProvider>
  )
}

export default App;
