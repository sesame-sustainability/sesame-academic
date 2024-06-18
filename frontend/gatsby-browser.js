/**
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

import "./src/css/index.css";
import React from "react";
import Layout from "./src/components/main";
import { AppContextProvider } from "./src/components/appState"
import * as Sentry from "@sentry/gatsby";

const FallbackComponent = () => (
  <div>An error has occurred. Please refresh the page.</div>
);

const ElementWithErrorBoundary = ({ element }) => (
  <Sentry.ErrorBoundary fallback={FallbackComponent} showDialog>
    {element}
  </Sentry.ErrorBoundary>
);

const wrapPageElement = ({ element, props }) => {
  if (
    props.location &&
    props.location.pathname &&
    (props.location.pathname === "/" ||
      props.location.pathname.includes("covid"))
  ) {
    return (
      <Layout {...props}>
        <ElementWithErrorBoundary element={element} />
      </Layout>
    );
  }
  return <ElementWithErrorBoundary element={element} />;
};

export const wrapRootElement = AppContextProvider;

export { wrapPageElement };
