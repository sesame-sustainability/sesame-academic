import { IndexedDBProps } from "react-indexed-db";

export const DatabaseConfig: IndexedDBProps = {
  name: 'SesameDB',
  version: 5,
  objectStoresMeta: [
    {
      store: 'savedCases',
      storeConfig: { keyPath: 'id', autoIncrement: true },
      storeSchema: [
        { name: 'type', keypath: 'type', options: { unique: false } },
        // { name: 'createdAt' keypath: 'createdAt', },
      ]
    }
  ]
};

export type savedCases = {
  id: number;
  type: string;
  createdAt: Date;
  name: string;
  analysisResult: object; // this will depend on which type of saved run it is - e.g. grid, fleet, etc.
}