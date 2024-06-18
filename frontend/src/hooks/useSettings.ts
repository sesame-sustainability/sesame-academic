import { useLiveQuery } from "dexie-react-hooks";
import * as React from "react"
import { AppContext } from "../components/appState";
import { db } from "./useDB";

export const useSettings = (): UserSetting[] => {

  const settings = useLiveQuery(
    () => {
      return db.settings.toArray()
    },
    [],
    [],
  ) as UserSetting[]

  return settings
}

export const setSettingTo = (id: string, value: UserSettingValue) => {
  db.settings.update(id, { value })
}

/**
 * Returns the value of a user setting.
 *
 * @param {string} id The setting id.
 * @return {boolean | undefined | null} Returns null while the setting is being fetched from the database, and otherwise returns undefined (if there's no set value in the databse) or boolean (if there is).
 */
export const useSetting = (id: string): [UserSettingValue, (value: UserSettingValue) => void] => {
  // const { settings } = React.useContext(AppContext);
  // const setting = settings?.find(setting => setting.id === id)?.value;
  
  const setting = useLiveQuery(
    () => {
      return db.settings.get(id)
    },
    [],
    null
  )

  const valueToReturn = setting === null ? null : setting?.value;

  const setSetting = (value: UserSettingValue) => setSettingTo(id, value)

  return [valueToReturn, setSetting];
}

export const useSettingValue = (id: string) => {
  const [setting, setSetting] = useSetting(id);
  return setting;
}

