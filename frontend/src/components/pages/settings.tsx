import { RouteComponentProps } from "@reach/router"
import * as React from "react"
import { setSettingTo } from "../../hooks/useSettings"
import Accordion from "../accordion"
import { AppContext } from "../appState"
import Layout from "../layout"
import SEO from "../seo"
import { Toggle } from "../toggle"

export const Settings = (props: RouteComponentProps): JSX.Element => {
  
  const { settings } = React.useContext(AppContext);

  const setSetting = (id: string, value: boolean) => {
    setSettingTo(id, value);
  }

  const visibleSettings = settings.filter(s => !s.hidden);
  
  return (
    <Layout
      {...props}
      type="page"
    >
      <SEO title="Settings" />
      {/* <div className="gutter-x mt-1 mb-3"> */}
        <div className="space-y-4 mt-8">
          {visibleSettings?.filter(s => !s.isAdvanced).map(({ id, value, label }) => {
            return (
              <Toggle
                key={id}
                id={id}
                label={label}
                value={value}
                setValue={(value) => setSetting(id, value)}
              />
            )
          })}
        </div>
        {process.env.NODE_ENV === 'development' &&
          <Accordion wrapperClassName="mt-7" theme="subtle" title="Advanced" padContentTop={true}>
            <div className="space-y-3">
              {visibleSettings?.filter(s => s.isAdvanced).map(({ id, value, label }) => {
                return (
                  <Toggle
                    key={id}
                    id={id}
                    label={label}
                    value={value}
                    setValue={(value) => setSetting(id, value)}
                  />
                )
              })}
            </div>
          </Accordion>
        }
      {/* </div> */}
      
    </Layout>
  )
}