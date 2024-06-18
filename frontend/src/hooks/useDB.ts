import * as React from "react"
import Dexie, { PromiseExtended, Table } from 'dexie'
import relationships from 'dexie-relationships'
import { useLiveQuery } from "dexie-react-hooks";
import * as Sentry from "@sentry/browser"
import { isBrowser } from '../utils';
import getDemoCases from "../data/demoCases"
import { demoBatches } from "../data/demoBatches";
import useAuth from "./useAuth"
import { atom, useAtom } from "jotai"

const databaseCollections = [
  {
    name: 'savedCases',
    fieldsToIndex: `++id, type`,
  },
  {
    name: 'savedCaseData',
    fieldsToIndex: `++id, savedCaseId -> savedCases.id`,
  },
  {
    name: 'savedBatches',
    fieldsToIndex: `++id, type`
  },
  {
    name: 'settings',
    fieldsToIndex: `++id`,
  }
] as Array<{
  name: DatabaseCollectionName;
  fieldsToIndex: string;
}>;

export const db = new Dexie('SESAME_DB', { addons: [ relationships ] }) as Dexie & {
  [key: string]: Table;
};

// NOTE: Don’t declare all columns like in SQL. You only declare properties you want to index, that is properties you want to use in a where(…) query.

const stores = databaseCollections.reduce((acc, collection) => {
  acc[collection.name] = collection.fieldsToIndex;
  return acc;
}, {} as {[key: string]: any})

db.version(12).stores(stores)

const defaultSettings: UserSetting[] = [
  {
    id: 'expandInputAccordionsByDefault',
    label: 'Expand input groups by default',
    value: false,
  },
  {
    id: 'dynamicallyFetchModuleMetadata',
    label: 'Dynamically fetch module metadata (not recommended)',
    value: false,
    isAdvanced: true,
  },
  {
    id: 'isNonCommercialUser',
    label: 'I am a non-commercial user',
    hidden: true,
    value: false,
  },
  {
    id: 'hasDismissedWelcomeModal',
    label: 'Has dismissed welcome modal',
    hidden: true,
    value: false,
  },
]

if (typeof window === 'object') {
  window.clearSettings = () => {
    db.settings.clear()
  }
}

const initializeDefaultSettings = () => {
  defaultSettings.forEach(defaultSetting => {
    db.settings.add(defaultSetting).catch((e) => {
      // console.log(`Setting `)
    });
  });
}

const hasInitializedDBAtom = atom<boolean>(false)

export const useInitializeDB = () => {

  const { isAuthenticated } = useAuth()
  const [hasInitializedDB, setHasInitializedDB] = useAtom(hasInitializedDBAtom)

  React.useEffect(() => {
    if (isBrowser() && isAuthenticated && !hasInitializedDB) {
      initializeDefaultSettings()
      initializeDemoContent().then(() => {
        setHasInitializedDB(true)
      })
    }
  }, [isAuthenticated])

  return hasInitializedDB
}

export const demoTag = ' (demo)'

/**
 * Copy demo cases and batches from JS files to indexedDB on app load (wipe first)
 */
const initializeDemoContent = () => {
  console.log('initializeDemoContent')

  // const demoCases = React.createRef()
  
  db.savedCases.filter(savedCase => savedCase.isDemo).delete()
  db.savedCaseData.filter(savedCaseData => savedCaseData.isDemo).delete()
  db.savedBatches.filter(savedBatch => savedBatch.isDemo).delete();

  const demoCasePopulationPromises: PromiseExtended<number | void>[] = []

  // console.log(demoCases)
  // console.log(demoCases.current)

  // if (!demoCases?.length) return null
  
  getDemoCases().forEach((demoCase, index) => {
    delete demoCase.id;
    delete demoCase.savedCaseId;
    delete demoCase.data?.savedCaseId;
    delete demoCase.isUnsaved;
    demoCasePopulationPromises.push(
      db.savedCases.put({
        ...demoCase,
        name: demoCase.name + demoTag,
        isFocusModeActive: demoCase.focusedInputs?.length > 0,
        isDemo: true,
        createdAt: typeof demoCase.createdAt === 'string' ? new Date(demoCase.createdAt) : demoCase.createdAt,
      }).then(id => {
        db.savedCaseData.put({
          ...demoCase.data,
          savedCaseId: id,
          isDemo: true,
        });
      })
    )
  });

  // after populating demo cases, then do demo batches
  return Promise.all(demoCasePopulationPromises).then(() => {
    demoBatches.forEach(async demoBatch => {
      const caseNamesWithDemoTag = demoBatch.caseNames.map(caseName => `${caseName}${demoTag}`)
      const casesInBatch = await db.savedCases.filter(savedCase => caseNamesWithDemoTag.includes(savedCase.name)).toArray()
      const caseIds = casesInBatch?.map(savedCase => savedCase.id)
      if (caseIds.length === demoBatch.caseNames.length) {
        const batchToInsert = {
          ...demoBatch,
          type: casesInBatch?.[0]?.type,
          name: `${demoBatch.name}${demoTag}`,
          caseIds,
          isDemo: true,
        }
        db.savedBatches.put(batchToInsert);
      } else {
        Sentry.captureEvent({
          message: 'Error inserting demo batch into database',
          extra: {
            batchName: demoBatch.name,
            reason: 'One or more of this batch\'s cases were not in the database when trying to add the demo batch',
          }
        })
        console.error(`One or more of demo batch "${demoBatch.name}" cases are missing from the database`)
      }
    });
  })
  // })

  
}

export const useSavedCases = (type?: string) => { 
  return useLiveQuery(
    () => {
      if (type) {
        return db.savedCases.where('type').equals(type).sortBy('id')
      } else {
        return null
      }
    },
    [] // dependencies list here - currently doesn't depend on anything, but if we abstract this we'll need to set 'type' as dynamic type prop, in which case add that to deps array
  )
}

export const promptUniqueBatchNameForModule = async (type: string | undefined, isRedo?: boolean): Promise<string | null> => {
  if (!type) {
    return null;
  }
  let name = prompt(isRedo ? 'That name already exists. Please choose another:' : 'Choose a name:');
  if (!name) {
    return null;
  }
  const doesNameExistAlready = !!(await db.savedBatches.get({name, type}));
  if (doesNameExistAlready) {
    name = await promptUniqueBatchNameForModule(type, true);
    return name;
  } else {
    return name;
  }
}

const doesSavedCaseNameExistForModule = async (name: string, moduleType: string, subModuleType: string, ) => {
  const query: any = { name: name, type: moduleType }
  if (subModuleType) {
    query.subModuleType = subModuleType;
  }
  const doesNameExistAlready = !!(await db.savedCases.get(query));
  // console.log(savedCaseWithThisName);
  return doesNameExistAlready;
  // return typeof savedCaseWithThisName === 'object';
}

export const getUniqueIncrementedCaseNamesForModule = async ({
  startingNumber = 1,
  startingName,
  moduleType,
  subModuleType,
  numCases,
  // namesArray,
}: {
  startingNumber?: number;
  startingName: string;
  moduleType: string;
  subModuleType?: string;
  numCases: number;
}): Promise<string[]> => {

  let lastUsedCaseNumber = startingNumber;
  const validCaseNames: string[] = [];

  while (validCaseNames.length < numCases) {
    while (await doesSavedCaseNameExistForModule(
      `${startingName} ${lastUsedCaseNumber}`,
      moduleType,
      subModuleType,
    )) {
      lastUsedCaseNumber++;
    }
    validCaseNames.push(`${startingName} ${lastUsedCaseNumber}`);
    lastUsedCaseNumber++;
  }

  return validCaseNames;
}