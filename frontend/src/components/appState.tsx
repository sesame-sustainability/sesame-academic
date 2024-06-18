import * as React from "react"
import { useSettings } from "../hooks/useSettings";

export const AppContext = React.createContext<{
  settings: UserSetting[];
  // updateSettings: () => void;
}>({settings: []});

const Provider = (props) => {

  const settings = useSettings();

  return (
    <AppContext.Provider value={{
      settings,
      // updateSettings
    }}>
      {props.children}
    </AppContext.Provider>
  )
};

export const AppContextProvider = ({ element }) => (
  <Provider>
    {element}
  </Provider>
);