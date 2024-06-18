import { v4 as uuidv4 } from "uuid";
export type State = {
  startsWith: string;
  stageId: number;
  pathwayName: string;
  pathwayId: string;
  lastSetBy: Actor;
  allOptions: AllOptionsState;
  userJson: UserJsonState;
  category?: Category;
  sourceId?: string;
  activityId?: string;
  fetchResponse?: PathwayAnalysisResponse & { data: Data[] };
  mode: Mode;
  showModal: boolean;
};

const create: Mode = "create";

export const initialState = (pathwayId: string): State => ({
  pathwayId,
  startsWith: "enduse",
  stageId: 0,
  activityId: undefined,
  category: undefined,
  sourceId: undefined,
  pathwayName: "",
  lastSetBy: "app",
  allOptions: {},
  userJson: {},
  mode: create,
  showModal: false,
});

export type Action =
  | {
      type: "setFetchResponse";
      response: PathwayAnalysisResponse & { data: Data[] };
    }
  | { type: "setMode"; mode: "create" | "edit" }
  | { type: "showModal"; isShown: boolean }
  | {
      type: "setOptions";
      options: AllOptionsState;
    }
  | {
      type: "setPathwayName";
      value: string;
    }
  | {
      type: "setStageFromBreadcrumb";
      index: number;
    }
  | {
      type: "setSourceId";
      id: string | undefined;
    }
  | {
      type: "skipStage";
      index: number;
    }
  | {
      type: "setTitleLastSetBy";
      actor: Actor;
    }
  | {
      type: "setCategoryForEdit";
      category: string;
    }
  | {
      type: "setStartsWithEdit";
      stage: "enduse" | "upstream";
    }
  | {
      type: "createNewPathway";
    }
  | {
      type: "setActivityId";
      id: string | undefined;
    }
  | {
      type: "setCategory";
      category: string | undefined;
    }
  | {
      type: "setNextStage";
    }
  | {
      type: "setUserInputMetadata";
      userInputs: UserInputProperties[];
      index: number;
    }
  | {
      type: "setStartsWith";
      stage: "enduse" | "upstream";
    }
  | {
      type: "setSelectionAndInputs";
      json: UserJsonState;
    };

export function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "setFetchResponse":
      return { ...state, fetchResponse: action.response };
    case "setOptions":
      return { ...state, allOptions: action.options };
    case "setPathwayName":
      return { ...state, pathwayName: action.value };
    case "setMode":
      return { ...state, mode: action.mode };
    case "showModal":
      return { ...state, showModal: action.isShown };
    case "setSourceId":
      return { ...state, sourceId: action.id };
    case "setActivityId":
      return { ...state, activityId: action.id };
    case "setTitleLastSetBy":
      return { ...state, lastSetBy: action.actor };
    case "setCategoryForEdit":
      return { ...state, category: action.category as Category };
    case "setCategory": {
      const newState = initialState(uuidv4());
      return {
        ...newState,
        lastSetBy: state.lastSetBy,
        pathwayName: state.pathwayName ?? newState.pathwayName,
        category: action.category as Category,
      };
    }
    case "setStartsWith":
      return { ...initialState(uuidv4()), startsWith: action.stage };
    case "setStartsWithEdit":
      return { ...state, startsWith: action.stage };
    case "skipStage":
      return {
        ...state,
        stageId: action.index + 1,
        userJson: { ...state.userJson, [action.index]: { skip: true } },
      };
    case "setStageFromBreadcrumb": {
      return {
        ...state,
        stageId: action.index,
        activityId: state.userJson[action.index].activity,
        sourceId: state.userJson[action.index].source,
      };
    }
    case "setNextStage":
      if (state.stageId + 1 > 5) return state;
      return {
        ...state,
        sourceId: state.userJson[state.stageId + 1]?.source,
        activityId: state.userJson[state.stageId + 1]?.activity,
        stageId: state.stageId + 1,
        userJson: {
          ...state.userJson,
          [state.stageId + 1]: {},
        },
      };
    case "setUserInputMetadata":
      return {
        ...state,
        userJson: {
          ...state.userJson,
          [action.index]: {},
        },
      };
    case "createNewPathway":
      return {
        mode: create,
        startsWith: "enduse",
        pathwayId: uuidv4(),
        stageId: 0,
        activityId: undefined,
        category: undefined,
        sourceId: undefined,
        pathwayName: "",
        lastSetBy: "app",
        allOptions: {},
        userJson: {},
        showModal: false,
      };
    case "setSelectionAndInputs":
      return {
        ...state,
        userJson: action.json,
      };
    default:
      throw new Error();
  }
}
