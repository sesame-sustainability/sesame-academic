import { ChartOptions, YAxisOptions } from "highcharts";
import React from "react";
import { Series } from "./components/figures";
import { PathwayCreatorState } from "./components/pathwayCreator1Page";

declare module "twin.macro";
declare module "gatsby-plugin-mailchimp";
declare module "react-lite-youtube-embed";
declare module "use-query-string";

declare global {
  type Category = "Electricity" | "Chemical" | "Fuel";
  type Mode = "create" | "edit";
  type Actor = "app" | "user";

  interface MailChimpResponse {
    result: "success" | "error";
    msg: string;
  }

  type AnalysisDirectionTuple = ["upstream", "enduse"];
  type AnalysisDirection = AnalysisDirectionTuple[number];
  type AnalysisYearsTuple = ["2016", "2017", "2018", "2019", "2020", "2021"];
  type AnalysisYears = AnalysisYearsTuple[number];
  type BalancingAreaTuple = [
    "CISO",
    "ERCO",
    "SWPP",
    "MISO",
    "NYIS",
    "FPL"
    // "PJM",
    // "ISNE",
  ];
  type Edges = {
    edges: DataPoint[];
  };
  type BalancingArea = BalancingAreaTuple[number]; // union type

  type StateAtStage = {
    links: Link[];
    activity: string;
    source: string;
    userInput: Record<string, InputState>;
    category: string;
    skip: boolean;
    activityOptions: Activity[];
    isComplete: boolean;
    userInputMetadata: UserInputProperties[];
  };
  type UserJsonState = Record<string, StateAtStage>;

  interface AllOptionsState {
    [key: string]: { [key: string]: string[] };
  }

  interface SinglePathway {
    category: Category;
    startsWith: "enduse" | "upstream";
    userJson: UserJsonState;
    allOptions: AllOptionsState;
    pathwayName: string;

    lastUpdated: number; // seconds since UNIX epoch
    fetchResponse?: PathwayAnalysisResponse & { data: Data[] };
  }
  interface PathwayState {
    [pathwayId: string]: SinglePathway;
  }
  type DataPoint = {
    node: {
      Balancing_Authority: BalancingArea;
      Date: string;
      Total_Interchange__MW_: string;
      Demand__MW_: string;
      Net_Generation__MW_: string;
    };
  };
  type Data = { [key: string]: string | number };
  type Entity = {
    id: string;
    name: string;
  };

  type Conditional = { args: (string | string[])[]; name: string };

  type Option = {
    value: string;
    conditionals: Conditional[];
  };

  type Validator = {
    name: string;
    args: number[];
    message?: string;
    warning: boolean;
  };

  type TooltipData = {
    content?: string;
    source?: string;
    source_link?: string;
  }

  type OnChangeAction = {
    type: string,
    target: string,
    value: string,
  }

  type UserInputProperties = {
    categorical: boolean;
    label: string;
    unit?: string;
    name: string;
    validators: Validator[];
    conditionals: Conditional[];
    defaults: {
      conditionals: Conditional[];
      value: string;
    }[];
    options?: Option[];
    display_options?: DisplayOptions;
    tooltip: TooltipData;
    children: UserInputProperties[];
    type: string;
    columns?: string[];
    rows?: UserInputProperties[];
    cells?: UserInputProperties[];
    on_change_actions?: OnChangeAction[];
  };
  type UserInput = UserInputProperties & {
    value: string;
  };
  type Source = Entity & {
    user_inputs: UserInputProperties[];
    version: number;
  };
  type Activity = Entity & {
    sources: Source[];
    category: string | null;
    product?: string | null;
    resources?: string[];
    products?: string[];
    product_types?: string[];
  };
  type Stage = {
    node: Entity & {
      activities: Activity[];
      categories: Category[];
    };
    activities?: Activity[];
    categories?: Category[];
    name?: string;
  };

  type Link = { node: { start: string; end: string; id: string } };

  type SensitivityInput = {
    name: string;
    label: string;
    default_value: string | number;
    minimizing_value: string | number;
    maximizing_value: string | number;
    min_value: number;
    max_value: number;
    unit: string?;
    data_lacking?: boolean;
  }

  type Sensitivity = {
    base_value: number;
    inputs: SensitivityInput[];
  }

  type TEAAnalysis = {
    id: string;
    analysis: {
      name: string;
      user_inputs: UserInputProperties[];
      unit?: string;
      pathway_id?: string[] | string[][];
    };
  };

  type TEAResponse = PathwayAnalysisResponse & {
    data: Data[];
  }

  type Axis = {
    name: string;
    type: string;
    label: string;
    unit: string;
  };

  type PowerSystemAnalysis = {
    id: string;
    system: {
      name: string;
      user_inputs: UserInputProperties[];
      axes: {
        x: string;
        y: Axis[];
      };
    };
  };

  type LCAIndicator = {
    id: string;
    value: string;
    label: string;
  };

  type Analysis = Entity & {
    label: string;
    params: {
      label: string;
      name: string;
      options: {
        label: string;
        value: string;
      }[];
    }[];
  };
  type PathwayAnalysisResponse = {
    columns: string[];
    title: string;
    unit: string;
    value: string;
    table?: (string | number)[][];
    sensitivity?: Sensitivity;
  };

  interface Pathway {
    [stageName: string]: {
      activityId: string;
      sourceId: string;
      userInputs: {
        [inputName: string]: {
          value?: string;
          isValid?: boolean;
          options?: string[];
        };
      };
    };
  }

  type FleetMetadata = {
    user_inputs: UserInputProperties[];
  };

  type GenerationShare = {
    pgm: string;
    region: string;
    power_source: string;
    values: (number | null)[];
  };

  type GridMetadata = {
    user_inputs: UserInputProperties[];
    generation_shares: GenerationShare[];
    power_source: string[];
  };

  type PpsMetadata = {
    user_inputs: UserInputProperties[];
  };

  type BasicModuleMetadata = {
    user_inputs: UserInputProperties[];
    hash: string;
    version: number;
  }

  // COVID Dashboard Types
  type PathwayAnalysisResponseWithUnformattedData = PathwayAnalysisResponse & {
    data: (string | number)[][];
  };

  interface CovidCaseNode {
    Cases: string;
    Date: string;
  }
  interface PeakEIA {
    edges: {
      node: { Summed_peak_hourly_Demand__MW_: string; Data_Date: string };
    }[];
  }

  interface AverageDailyPeak {
    nodes: { Avg_daily_peak: string }[];
  }

  // comparison cases

  type ModuleGroup = 'systems' | 'paths'

  type ComparableResultsModuleProps = {
    title: string;
    path: string;
    type: string;
    group: ModuleGroup;
    description: string;
    buttonText?: string;
    allowComparisons?: boolean;
    maxComparisonCases?: number;
    allowCaseDuplication?: boolean;
    showRunAllButton?: boolean;
    allowChartTiling?: boolean;
    apiPath?: string; // this is the root api path for the module
    component: () => JSX.Element;
  }

  type ComparisonCaseBatch = {
    id: number;
    caseIds: number[];
    name: string;
    createdAt?: Date;
    type: string;
    isDemo?: boolean;
    isFocusLinkActive?: boolean;
    // focusedInputs?: string[];
  }

  type SavedCaseData = {
    savedCaseId?: number;
    isDemo?: boolean;
    analysisResult?: any;
    customData: any; // TODO make this stricter
    // inputGroupOpenStates?: Record<string, boolean>;
    inputValues?: Record<string, string> | null;
    moduleVersion: number;
    // isStale?: boolean; // if it's an outdated case, i.e. uses an old module version
  }

  type StageInputData = {
    inputValues: Record<string, string>;
    nodeChosen: string;
    moduleVersion: number;
  }

  type SavedCaseDataPaths = SavedCaseData & {
    customData?: {
      inputValuesByStage?: StageInputData[];
      customInputValues?: {
        additionalBackendInputValues?: Records<string, string>;
        dataSourcesChosen: Array<string | null>;
        selectedProduct: string;
        selectedProductType: string;
        selectedResource: string;
        startWith: string;
      }
    };
  }

  type ComparisonCase = {
    data?: SavedCaseData;
    isRunning?: boolean;
    isLoading?: boolean;
    isUnsaved?: boolean;
    id: number;
    name?: string;
    isSelectedForEditing?: boolean;
    savedCaseId?: number;
    isDemo?: boolean;
    // isStale?: boolean;
    focusedInputs?: string[];
    isFocusModeActive: boolean;
    // inputGroupOpenStates: Record<string, boolean>;
  }

  type ModuleStateProps = {
    isAnyColumnFullscreened?: boolean;
    numChartCols?: number;
    comparisonCases: ComparisonCase[];
    isComparisonMode: boolean;
    isFocusLinkActive: boolean;
    chartControlAllocation: 'individual' | 'group';
    allowComparisons?: boolean;
    maxComparisonCases: number;
    allowCaseDuplication: boolean;
    showRunAllButton: boolean;
    allowChartTiling?: boolean;
    headerTitle: string | null,
    apiPath?: string,
    type: string,
    subModuleType?: string,
    savedBatch?: ComparisonCaseBatch;
  }

  type ModuleActionProps = {
    type: string;
    value?: any;
    index?: number;
    dispatch?: React.Dispatch<ModuleActionProps>
    options?: {
      isFocusLinkingDisabled?: boolean
    }
  }

  type ModuleDispatch = {
    dispatch: React.Dispatch<ModuleActionProps>
  }

  // TODO finish typescripting dispatch/reducer in comparableResultsModule.tsx
  // type ModuleActionProps = 
  //   | { type: 'setColumnFullscreen', value: boolean }
  //   | { type: 'setNumChartCols', value: number }
  //   | { type: 'addComparisonCol' }
  //   | { type: 'setIsCaseLoadingAtIndex', value: boolean, index: number }
  //   | { type: 'setComparisonCaseIdAtIndex', value: 'unsaved' | number | null, index: number } & ModuleDispatch
  //   | { type: 'loadBatchId', value: number } & ModuleDispatch
  //   | { type: 'setBatch', value: ComparisonCaseBatch }
  //   | { type: 'setBatchProps', value: Partial<ComparisonCaseBatch> }
  //   | { type: 'deleteSavedBatchIds', value: number[] }
  //   | { type: 'enableErroneousInputHighlightingAtIndex', index: number }

  interface InputState {
    value: string;
    error: string;
    warning: string;
    isVisible: boolean;
    options: string[];
    isFocused?: boolean;
    wasJustManuallyCleared?: boolean;
  }

  type SetInputOptions = {
    dontClearComparisonCase?: boolean;
    isBlur?: boolean;
    isFocused?: boolean;
    wasJustManuallyCleared?: boolean;
  }

  type InputGroup = {
    title?: string;
    userInputs: UserInputProperties[];
  };

  type UnifiedLCATEAComparisonCaseInputHandler = {
    nodesChosen: Array<string | null>;
    arrayOfStageInputHandlers: InputHandler[];
    customInputStates: Record<string, string>;
    additionalBackendInputValues: Record<string, boolean>;
    pathwayCreatorState: PathwayCreatorState;
    // setPathwayCreatorState: React.Dispatch<React.SetStateAction<PathwayCreatorState>>;
  }

  type InputHandler = {
    inputStates: Record<string, InputState>;
    setInput: (name: string, value: string, opts?: SetInputOptions) => void;
    isValid: boolean;
    setInputError: (inputName: string, error: string) => void;
  }
  interface DisplayOptions {
    label_size?: 'large',
    indent_level?: 1 | 2 | 3,
  }

  type APIRequest = {
    endpoint: string;
    body: any;
  }

  type APIRequestWithType = APIRequest & {
    type: string;
  }

  type UserSettingValue = boolean | null | undefined

  type UserSetting = {
    id: string;
    label: string;
    value: UserSettingValue;
    isAdvanced?: boolean;
    hidden?: boolean;
  }

  type UserProfile = {
    name: string;
    institution: string;
  }

  type ChartOptionsWithSeries = {
    series: Series[];
    yAxis?: YAxisOptions[];
  } & ChartOptions

  type DatabaseCollectionName = 'savedCases' | 'savedCaseData' | 'savedBatches' | 'settings';

  type SavedItemCollectionName = 'savedCases' | 'savedBatches' | 'demoCases' | 'demoBatches'
}

