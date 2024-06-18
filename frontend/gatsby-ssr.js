/**
 * Implement Gatsby's SSR (Server Side Rendering) APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/ssr-apis/
 */

import "./src/css/index.css";
import React from "react";
import Layout from "./src/components/main";

const wrapPageElement = ({ element, props }) => {
  if (
    props.location &&
    props.location.pathname &&
    (props.location.pathname === "/" ||
      props.location.pathname.includes("covid"))
  ) {
    return <Layout {...props}>{element}</Layout>;
  }
  return element;
};

export { wrapPageElement };

// Create top-level div for React.Portal
export const onRenderBody = ({ setPostBodyComponents }, pluginOptions) => {
  setPostBodyComponents([
    <div
      key={pluginOptions.key ? pluginOptions.key : "portal"}
      id={pluginOptions.id ? pluginOptions.id : "portal"}
    >
      {pluginOptions.text}
    </div>
  ]);
};
