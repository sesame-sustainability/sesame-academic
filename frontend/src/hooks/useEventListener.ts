import * as React from "react"

export const useEventListener = (
  eventType: string,
  callback: (e: any) => void
) => {
  React.useEffect(() => {
    document.addEventListener(eventType, callback);
    return () => {
      document.removeEventListener(eventType, callback);
    }; 
  });
}
