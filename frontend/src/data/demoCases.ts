/**
 * SOP for exporting demo cases:
 * 
 * - Run the case as spec'd
 * - Save it with the correct name
 * - Close and open it
 * - JSON.stringify(state) in <ComparableResultsModule>
 * - Paste into editor and prettify
 * - Copy/paste comparison case objects into this file
 * - remove id (we'll programmatically generate this when populating DB)
 * - update createdAt to use new Date(...) format
 *     - REGEX find/replace:
 *       "createdAt": (.*?),
 *       "createdAt": new Date($1),
 * - remove savedCaseId and id from data
 * - Add focusedInputs array to each case [WAIT - focusedInputs is specified in batches, not cases... what to do here? Need to be able to specify focusedInputs in each case...]
 * - Update case IDs
 * - Close/open app in private window and make sure they get propagated to DB correctly, with results and focused inputs
 */

import { carsDemoCases } from "./demoCasesCars";
import { hydrogenDemoCases } from "./demoCasesHydrogen";
import { pathsElectricityDemoCases } from "./demoCasesPathsElectricity";
import { powerGreenfieldDemoCasesTX } from "./demoCasesPowerGreenfieldTX";
import { powerGreenfieldDemoCasesCA } from "./demoCasesPowerGreenfieldCA";
import { congressDemoCases } from "./demoCasesCongress";
import { demoCasesCarsCA } from "./demoCasesCarsCA";
import { powerGreenfieldDemoCasesTX2 } from "./demoCasesPowerGreenfieldTX2";
import { powerGreenfieldDemoCasesCA2 } from "./demoCasesPowerGreenfieldCA2";
import { powerGreenfieldDemoCasesFL } from "./demoCasesPowerGreenfieldFL";
import { powerGreenfieldDemoCasesRegional } from "./demoCasesPowerGreenfieldRegional";

const getDemoCases = () => ([
  ...carsDemoCases,
  ...hydrogenDemoCases,
  ...pathsElectricityDemoCases,
  ...congressDemoCases,
  ...demoCasesCarsCA,
  ...powerGreenfieldDemoCasesTX,
  ...powerGreenfieldDemoCasesCA,
  ...powerGreenfieldDemoCasesTX2,
  ...powerGreenfieldDemoCasesCA2,
  ...powerGreenfieldDemoCasesFL,
  ...powerGreenfieldDemoCasesRegional,
]);

export default getDemoCases