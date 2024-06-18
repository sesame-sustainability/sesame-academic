import * as React from "react"

export const useMount = (func: () => void) => {
  React.useEffect( () => func(), []);
}

export const useUnmount = (func: () => void) => {
  React.useEffect( () => () => func(), [] );
}