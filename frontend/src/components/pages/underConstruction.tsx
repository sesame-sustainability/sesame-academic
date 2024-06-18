import * as React from "react"
import Layout from "../layout"
import { ChartTitle } from "../styles"

export const UnderConstruction = () => {
  return (
    <Layout hideRibbon={true}>
      <ChartTitle className="text-left">Under Construction</ChartTitle>
    </Layout>
  )
}