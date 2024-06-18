import React from "react";
import * as Styles from "./styles";
import { CategoricalSelect } from "./appSelects";
import Accordion from "./accordion";
import { ShareTable } from "./shareTable";
import { Tooltip } from "./tooltip";
import { ModuleDispatchContext, ModuleStateContext } from "./comparableResultsModule";
import { useSetting, useSettingValue } from "../hooks/useSettings";
import { Toggle } from "./toggle";
import { trigger } from "../utils/events";
import { useEventListener } from "../hooks/useEventListener";
import { EyeIcon } from "@heroicons/react/solid";
import { customAlert } from "./customAlert";

// const isUserInputEqual = (prevProps, nextProps) => {
//   if (nextProps.userInput.type === 'share_table') {
//     // return false;
//     const dependentInputNames = unique(
//       flattenDeep(nextProps.userInput?.rows?.map(row => {
//         return row?.cells?.map(cell => {
//           return cell?.defaults?.map(defawlt => {
//             return defawlt.conditionals.map(conditional => {
//               return conditional.args?.[0];
//             })
//           });
//         });
//       }))
//     );
//     return dependentInputNames?.every(name => {
//       prevProps?.inputStates[name].value === nextProps?.inputStates[name].value;
//     })
//   }
//   return JSON.stringify(prevProps?.inputState) === JSON.stringify(nextProps?.inputState);
// }

const userInputLabel = (userInput: UserInputProperties): string => {
  if (userInput.unit) {
    return `${userInput.label} (${userInput.unit})`;
  } else {
    return userInput.label;
  }
}

const UserInput = ({
  userInput,
  inputState,
  inputStates,
  setInput,
  setInputError,
  layout,
}: {
  userInput: UserInputProperties;
  inputState: InputState;
  inputStates: Record<string, InputState>;
  setInput: (name: string, value: string, opts?: SetInputOptions) => void;
  setInputError: (inputName: string, error: string) => void;
  layout?: UserInputLayoutOptions;
}): JSX.Element | null => {
  const {name, label, children, categorical, type, columns, rows} = userInput;
  const error = inputStates[name]?.error;
  const warning = inputStates[name]?.warning;
  // const isValid = inputStates[name]?.isValid;
  // const inputState = inputStates[name];
  const isValid = inputState ? !(inputState.isVisible && (!!error || inputState.value === "")) : undefined;

  const [canHighlightErroneousInputs, setCanHighlightErroneousInputs] = React.useState(false);

  React.useEffect(() => {
    setCanHighlightErroneousInputs(false)
    setTimeout(() => {
      setCanHighlightErroneousInputs(true)
    }, 1000)
  }, [inputStates])
  
  const errorClasses = canHighlightErroneousInputs ? '!border-red-600 !border-2' : '';

  if (!inputStates[name]?.isVisible) {
    return null;
  }

  return (
    <>
      <InputBlock userInput={userInput} layout={layout}>
        {(() => { 
          if (type === 'categorical' || type === 'options') {
            const inputOptions = inputStates[name]?.options;
            const isToggle = (
              inputOptions.length === 2 && inputOptions.includes('Yes') && inputOptions.includes('No')
              ||
              inputOptions.length === 1 && inputOptions.includes('Yes')
              ||
              inputOptions.length === 1 && inputOptions.includes('No')
            )
            if (isToggle) {
              return (
                <Toggle
                  id={name}
                  label=""
                  isErroneous={!isValid && canHighlightErroneousInputs}
                  isDisabled={inputOptions.length === 1}
                  value={inputStates[name]?.value === 'Yes'}
                  setValue={(value) => {
                    setInput(name, value ? 'Yes' : 'No');
                  }}
                />
              )
            }
          }         
          if (type === 'categorical') {
            const categoricalOpts = inputStates[name]?.options;
            return (
              <CategoricalSelect
                name={name}
                options={{ [name]: categoricalOpts }}
                value={inputStates[name]?.value || ""}
                className={!isValid ? errorClasses : ''}
                setTarget={(value) => {
                  if (setInput) {
                    setInput(name, value);
                  }
                }}
              />
            );
          }
          else if (type === 'options') {
            const inputOptions = inputStates[name]?.options;
            return (
              <CategoricalSelect
                key={name}
                name={name}
                options={{ [name]: inputOptions }}
                value={inputStates[name]?.value || ""}
                className={!isValid ? errorClasses : ''}
                setTarget={(value) => {
                  if (setInput) {
                    setInput(name, value);
                  }
                }}
              />
            );
          }
          else if (type === 'continuous') {
            return (
              <>
                <Styles.Input
                  key={name}
                  type="number"
                  isValid={!error}
                  id={`user-inputs--input-${name}`}
                  placeholder={label}
                  className={!isValid ? errorClasses : ''}
                  value={inputStates[name]?.value}
                  onBlur={(e) => {
                    e.target.value = inputStates[name]?.value
                    const value = e.target.value;                    
                    const parsedValue = JSON.parse(JSON.stringify(Number(value)));

                    if (JSON.stringify(parsedValue) !== value) {
                      const wasJustManuallyCleared = (value === ''); // this flag prevents refilling with default value if user deletes input value and unfocuses
                      let valueToSet = value;
                      if (value !== '') {
                        valueToSet = JSON.stringify(parsedValue);
                      }
                      setInput(name, valueToSet, { isFocused: false, wasJustManuallyCleared });//, {isBlur: true});
                    } 
                    else {
                      setInput(name, value, { isFocused: false });
                    }
                  }}
                  onChange={({
                    target: { value },
                  }: React.ChangeEvent<HTMLInputElement>) => {
                    console.log('onChange');
                    if (setInput) {
                      const isFocused = type === 'continuous'; // only need to track isFocused state for number inputs, to avoid bug where you delete the value in the input and it immediately gets replaced with the default value
                      setInput(name, value, { isFocused });
                    }
                  }}
                  // onFocus={(e) => {e.target.select();}}
                  // onMouseUp={() => {return false;}}
                />
                {error && (
                  <div className="absolute inset-y-0 -right-4 top-2 pr-8 flex items-start pointer-events-none">
                    <svg
                      className="h-5 w-5 text-red-500"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      />
                    </svg>
                  </div>
                )}
                {error && <Styles.InputMessage type="error" message={error} className="" inputName={name} /> }
                {warning && <Styles.InputMessage type="warning" message={warning} className="" inputName={name} /> }
            </>
            );
          }
          else if (type === 'share_table') {
            return (
              <>
                <ShareTable
                  userInput={userInput}
                  inputStates={inputStates}
                  setError={(msg: string) => setInputError(userInput.name, msg)}
                  setInput={setInput}
                  // linkedInput={'msps2'}
                  // onChangeActions={[{
                  //   type: 'set_input_to',
                  //   target: 'msps2',
                  //   value: 'User',
                  // }]}
                />
                {error && <Styles.InputMessage type="error" message={error} className="" inputName={name} /> }
                {warning && <Styles.InputMessage type="warning" message={warning} className="" inputName={name} /> }
              </>
            );
          }
          else {
            return null;
          }

        })()}
      </InputBlock>
    </>
  )
}

const FocusToggle = ({
  handleFocusIconClick,
  isFocused,
  isFocusModeActive,
  userInput,
}: {
  handleFocusIconClick: any;
  isFocused: boolean | undefined;
  isFocusModeActive: boolean | undefined;
  userInput: UserInputProperties;
}) => {
  return (
    <div
      className="relative mr-2 cursor-pointer group"
      onClick={() => handleFocusIconClick()}
      id={`focus--${userInput.name}`}
      title={
        isFocused
        ?
        (
          isFocusModeActive
          ?
          'Hide input'
          :
          'Input selected for focus mode. Click Focus button to hide all non-focused inputs.'
        )
        :
        'Select input for focus mode'
      }
    >
      <div
        className={`block border-2 ${isFocused ? 'border-gray-600' : 'group-hover:border-gray-300 border-gray-200'} transition-colors rounded-full`}
        style={{height: '16px', width: '16px'}}
      >
        <div className="bg-gray-600 rounded-full transition-opacity" style={{width: 8, height: 8, marginLeft: 2, marginTop: 2, opacity: isFocused ? 1 : 0}} />
      </div>
    </div>
  )
}

export const InputBlock = ({
  userInput,
  children,
  layout,
  className,
}: {
  userInput?: UserInputProperties;
  children?: React.ReactNode;
  layout?: UserInputLayoutOptions;
  className?: string;
}) => {

  const { comparisonCases } = React.useContext(ModuleStateContext)
  const { comparisonIndex, focusedInputs } = React.useContext(UserInputsContext)
  const dispatch = React.useContext(ModuleDispatchContext)

  const isFocusModeActive = typeof comparisonIndex === 'number' && comparisonCases?.[comparisonIndex]?.isFocusModeActive

  const isFocused = userInput && focusedInputs?.includes(userInput.name);

  const handleFocusIconClick = () => {
    if (userInput) {
      dispatch({type: 'toggleFocusInputAtCaseIndex', value: userInput.name, index: comparisonIndex})
    }
  }

  return (
    <div className={`grid ${layout === 'column' || userInput?.type === 'share_table' ? 'grid-cols-1 gap-1' : 'grid-cols-3 gap-4'} items-center mb-2 relative ${isFocusModeActive && !isFocused && userInput ? 'hidden' : ''} ${className ?? ''}`}>
      {userInput &&
        <Styles.Label
          className={`${layout !== 'column' && (userInput.type !== 'share_table') ? 'col-span-2' : ''} ${userInput.type === 'share_table' ? 'mt-2 mb-3' : ''}`}
          displayOptions={userInput.display_options}
          htmlFor={`user-inputs--${userInput.type}-${userInput.name}`}
        >
          {/* <div className="relative w-6 h-6 border border-gray-200 rounded-full mr-2">
            <div className="absolute top-[0.3rem] left-[0.3rem] w-3 h-3 rounded-full bg-gray-200"></div>
          </div> */}
          <FocusToggle
            handleFocusIconClick={handleFocusIconClick}
            userInput={userInput}
            isFocused={isFocused}
            isFocusModeActive={isFocusModeActive}
          />
          {/* <span className={`${isFocused ? 'font-bold' : ''}`}> */}
            {userInputLabel(userInput)}
          {/* </span> */}
          <Tooltip data={userInput.tooltip} />
        </Styles.Label>
      }
      {userInput?.type === 'share_table'
        ?
        <div className='col-span-2'>
          {children}
        </div>
        :
        children
      }
      
    </div>
  )
}

type UserInputLayoutOptions = 'column' | 'row';

export const checkConditional =
  (
    { args, name: conditionalName }: Conditional,
    currentInputStates: Record<string, InputState>,
    contextInputValues?: Record<string, string | boolean>,
  ) => {
    let [inputName] = args;
    let expectedValue = args[1];

    if (Array.isArray(inputName)) {
      inputName = inputName[0];
    }

    if (conditionalName === "context_equal_to") {
      if (Array.isArray(expectedValue)) {
        expectedValue = expectedValue[0];
      }
      return JSON.stringify(contextInputValues?.[inputName]) === JSON.stringify(expectedValue);
    }

    const dependentInput = currentInputStates[inputName];
    if (!dependentInput?.isVisible) {
      // conditional for dependent input is not passing
      // so this input should not pass either
      return false;
    }

    const inputValue = dependentInput?.value;

    if (conditionalName === "input_equal_to") {
      if (Array.isArray(expectedValue)) {
        expectedValue = expectedValue[0];
      }
      return inputValue === expectedValue;
    } else if (conditionalName === "input_not_equal_to") {
      if (Array.isArray(expectedValue)) {
        expectedValue = expectedValue[0];
      }
      return inputValue !== expectedValue;
    } else if (conditionalName === "input_included_in") {
      if (!Array.isArray(expectedValue)) {
        return true;
      }
      return expectedValue.includes(inputValue);
    }

    return true;
  }//,
//   [contextInputValues]
// );

type UserInputsContextState = {
  comparisonIndex: number;
  focusedInputs: string[];
}

const UserInputsContext = React.createContext<Partial<UserInputsContextState>>({})

const UserInputs = ({
  userInputs,
  comparisonIndex,
  inputStates,
  setInput,
  setInputError,
  layout,
  noWrapper,
  inputGroupOpenStates,
  toggleInputGroupOpenState,
  // wrapperClassName,
  // labelClassName,
  // selectClassName,
  // errorClassName,
}: {
  userInputs: UserInputProperties[];
  comparisonIndex?: number;
  inputStates: Record<string, InputState>;
  setInput: (name: string, value: string, opts?: SetInputOptions) => void;
  setInputError: (inputName: string, error: string) => void;
  layout?: UserInputLayoutOptions;
  noWrapper?: boolean;
  inputGroupOpenStates?: Record<string, boolean>;
  toggleInputGroupOpenState?: (name: string) => void;
  // wrapperClassName?: string;
  // labelClassName?: string;
  // selectClassName?: string;
  // errorClassName?: string;
}): JSX.Element | null => {
  if (!userInputs) return null;

  const { isComparisonMode, comparisonCases } = React.useContext(ModuleStateContext);
  // const { settings } = React.useContext(AppContext);
  const comparisonCase = comparisonCases?.[comparisonIndex];
  const isFocusModeActive = comparisonCase?.isFocusModeActive;
  const focusedInputs = comparisonCase?.focusedInputs;
  const dispatch = React.useContext(ModuleDispatchContext)

  let numHiddenInputs = 0;

  // calculate number of hidden inputs when in focus mode
  if (isFocusModeActive) {
    const incrementHiddenInputsIfHidden = (userInput: UserInputProperties) => {
      if ((userInput?.conditionals as Conditional[])?.every(conditional => checkConditional(conditional, inputStates))) {
        if (!focusedInputs?.includes(userInput.name)) {
          numHiddenInputs++
        }
      }
    }
    userInputs.map(userInput => {
      if (userInput.type === 'group') {
        userInput.children.map(userInput => {
          incrementHiddenInputsIfHidden(userInput)
        })
      } else {
        incrementHiddenInputsIfHidden(userInput)
      }
    })
  }

  // const numHiddenInputs = numVisibleInputsNotAccountingForFocusMode - (focusedInputs?.length || 0);
  const expandInputAccordionsByDefault = useSettingValue('expandInputAccordionsByDefault') ?? false;

  const html = (
    <UserInputsContext.Provider value={{
      comparisonIndex: comparisonIndex,
      focusedInputs: comparisonCases?.[comparisonIndex]?.focusedInputs,
    }}>
      {userInputs.map(userInput => {
        if (userInput.type === 'group') {
          // don't display this input group if any conditionals don't pass
          if ((userInput.conditionals as Conditional[])?.some(conditional => !checkConditional(conditional, inputStates))) {
            return null;
          }
          // hide this input group if we're in focus mode and none of its inputs are focused
          const areAnyFocusedInputs = userInput.children?.some(childInput => {
            return focusedInputs?.includes(childInput.name)
          })
          if (isFocusModeActive && !areAnyFocusedInputs) {
            return null;
          }

          const childInputElements = userInput.children?.map(childInput => {
            return (
              <UserInput
                userInput={childInput}
                inputStates={inputStates}
                inputState={inputStates?.[childInput.name]}
                setInput={setInput}
                setInputError={setInputError}
                layout={layout}
              />
            )
          });

          return (
            isFocusModeActive 
            ?
            childInputElements
            :
            <Accordion
              key={userInput.name}
              title={userInputLabel(userInput)}
              defaultOpen={expandInputAccordionsByDefault}
              isOpen={inputGroupOpenStates?.[userInput.name] ?? expandInputAccordionsByDefault}
              setIsOpen={(e) => {
                toggleInputGroupOpenState && toggleInputGroupOpenState(userInput.name);
              }}
              headerContentWhenClosed={
                <>
                  {areAnyFocusedInputs && <div className="ml-auto mr-2 rounded bg-gray-200 text-gray-500 text-sm py-[1px] px-2">Has focus selections</div>}
                </>
              }
              // isOpen={inputGroupOpenStates?.[userInput.name]}
              // setIsOpen={(e) => {
              //   dispatch({type: 'toggleInputGroupOpenStateAtComparisonIndex', value: userInput.name, index: comparisonIndex})
              // }}
              padContentTop={true}>
              <div className="grid grid-cols-1">
                {childInputElements}
              </div>
            </Accordion>
          )
        }
        else {
          // userInput.display_options = {label_size: 'large'}
          return (
            <UserInput
              userInput={userInput}
              inputStates={inputStates}
              inputState={inputStates?.[userInput.name]}
              setInput={setInput}
              setInputError={setInputError}
              layout={layout}
              key={userInput.name}
            />
          )
        }
        // const error = inputStates[name]?.error;
        // const warning = inputStates[name]?.warning;
        // if (!inputStates[name]?.isVisible) return null;
      })}
    </UserInputsContext.Provider>
    // </div>
  );
  return noWrapper
  ?
    html
  :
    <div className={isComparisonMode && !isFocusModeActive ? 'py-2' : ''}>
      {html}
    </div>
  ;
};

export default UserInputs;
