import React, { useMemo, useState, useEffect, useCallback } from "react";
import * as Sentry from "@sentry/browser";
import { roundToHundredth } from "../utils";
import useClient from "../hooks/useClient";
import { flatMap } from "lodash";
import { checkConditional } from "../components/userInputs";
import { atom, useAtom } from "jotai";

type RequestCacheItem = {
  request: string;
  response?: any;
}

const requestCacheAtom = atom<RequestCacheItem[]>([])

const useUserInputs = (
  userInputs?: UserInputProperties[],
  defaultSourceOrAnalysis?: string,
  path = "/pathway/sources",
  initialInputValues?: Record<string, string>,
  contextInputValues?: Record<string, string | boolean>,
  opts?: { isSourceRequired?: boolean },
): [
  Record<string, InputState>,
  (name: string, value: string, opts?: SetInputOptions) => void,
  boolean,
  React.Dispatch<React.SetStateAction<string | undefined>>,
  UserInputProperties[],
  (inputName: string, error: string) => void,
] => {
  const { client } = useClient();

  // const requestCache = React.useRef<RequestCacheItem[]>([])

  const [requestCache, setRequestCache] = useAtom(requestCacheAtom)

  useEffect(() => {
    // requestCache.current = [];
    setRequestCache([])
  }, [])

  const logRequestCacheStart = ({request}: {request: string}) => {
    // if (!requestCache.current.find(r => r.request === request))
      // requestCache.current.push({request});
    setRequestCache(oldCache => oldCache.concat({request}))
  }

  const logRequestCacheResponse = ({request, response}: {request: string, response: string}) => {
    // console.log('attempting to log request response:', request, response, requestCache)
    // console.log('setting cache resepnose actually')

    // requestCache.current = requestCache.current.map(item => {
    //   if (item.request === request) {
    //     return {
    //       ...item,
    //       response,
    //     }
    //   } else {
    //     return item;
    //   }
    // })

    setRequestCache(oldCache => [...oldCache].map(item => {
      if (item.request === request) {
        return {
          ...item,
          response,
        }
      } else {
        return item;
      }
    }))
  }

  const fetchRequestFromCache = (request: string) => {
    // return requestCache.current.find(r => r.request === request)?.response;

    return requestCache.find(r => r.request === request)?.response;
  }

  // flatten user_inputs nested hierarchy
  // let newUserInputs: UserInputProperties[] = [];
  // const newUserInputs: UserInputProperties[] = userInputs?.map(userInput => {
  //   userInput.children?.forEach(child => {
  //     childInputs.push(child);
  //   });
  //   return delete userInput.children
  // }).concat(childInputs)
  // userInputs = userInputs.

  if (userInputs) {
    userInputs = flatMap(userInputs, input => {
      return input.children?.length > 0 ? input.children : input
    })
  }

  // Set initial input state via userInputs and recompute
  // if the userInputs passed to the hook change
  const userInputsToState = useMemo(() => {
    return (
      userInputs?.reduce(
        (acc, cur) => {
          var inputState = {
            isVisible: true,
            value: initialInputValues ? (initialInputValues[cur.name] || "") : "",
            error: "",
            options: cur.options?.map((o) => o.value) || [],
          } as InputState;
          return ({
            ...acc,
            [cur.name]: inputState
          })
        },
        {}
      ) || {}
    );
  }, [userInputs, initialInputValues]);

  const [inputStates, setInputStates] =
    useState<Record<string, InputState>>(userInputsToState);
  const [sourceOrAnalysis, setSourceOrAnalysis] = useState<string | undefined>(
    defaultSourceOrAnalysis
  );

  useEffect(() => {
    if (
      initialInputValues
      || 
      (typeof initialInputValues === 'object' && Object.keys(initialInputValues).length === 0)
    ) {
      setInputStates(userInputsToState)
    }
  }, [initialInputValues])

  useEffect(() => {
    setSourceOrAnalysis(defaultSourceOrAnalysis);
  }, [defaultSourceOrAnalysis]);

  const checkConditionalOptimized = useCallback(
    (
      conditional: Conditional,
      currentInputStates: Record<string, InputState>,
    ) => {
      return checkConditional(conditional, currentInputStates, contextInputValues)
    },
    [contextInputValues]
  );

  const isStructurallyEqual = (a: string[], b: string[]) => {
    return JSON.stringify(a) === JSON.stringify(b);
  };

  const inputStateKeys = Object.keys(inputStates);
  const categoricalInputNames = userInputs?.filter(u => u.type === 'categorical').map(u => u.name);
  const categoricalInputStateKeys = inputStateKeys.filter(key => categoricalInputNames?.includes(key))
  // const categoricalInputStates = categoricalInputStateKeys.map(key => inputStates[key])
  
  // fetch categorical input options
  React.useEffect(() => {
    
    categoricalInputNames?.forEach(async (name) => {

      // console.log('attempting, input:', name)
      
      const categoricalIndexOfThisInput = categoricalInputStateKeys.indexOf(name);

      const categoricalInputKeysBeforeThisOne = categoricalInputStateKeys.slice(0, categoricalIndexOfThisInput)

      const doAllPreviousCategoricalInputsHaveValues = categoricalInputKeysBeforeThisOne
        .filter(key => inputStates[key].isVisible)
        .every(key => inputStates[key].value)

      // console.log('do all previous have values?', doAllPreviousCategoricalInputsHaveValues)

      // prevent condition where we'd try to fetch categorical input options in Paths builder, but source/pathway wasn't available here yet (=> 404)
      if (opts?.isSourceRequired && !sourceOrAnalysis) return;

      if (
        doAllPreviousCategoricalInputsHaveValues
        &&
        (!inputStates[name]?.value || !inputStates[name]?.options?.length)
      ) {

      // const result = useQuery(['categoricalInputOptions', ({name, options: inputStates[name]?.options})], async () => {

        // can I fetch all categorical inputs in this one useQuery?

        const queryParams = categoricalInputKeysBeforeThisOne
          .filter(key => inputStates[key].isVisible && inputStates[key].value && key !== name)
          .map(key => `${key}=${encodeURIComponent(inputStates[key].value)}`)
          .join('&')
      
        let url = `${path}`;
        if (sourceOrAnalysis) {
          url += `/${sourceOrAnalysis}`;
        }
        url += `/user_inputs/${name}`;

        const request = `${url}${
          queryParams !== "" ? `?${queryParams}` : ""
        }`;

        // if request is already started but not finished, skip
        const cacheItem = requestCache.find(r => r.request === request);
        if (cacheItem && !cacheItem.response) {
          // console.log(name, 'alreaady started, skipping')
          // console.log(requestCache)
          // console.log(cacheItem)
          return;
        }
        let data = fetchRequestFromCache(request);
        if (!data) {
          // console.log('fetching...', name)
          logRequestCacheStart({request})
          data = await client(request);
          logRequestCacheResponse({request, response: data})
        } else {
          // console.log('CACHE HIT!')
        }

        if (!Array.isArray(data?.options)) return;
        const options: string[] = data?.options || [];

        // if the options we just got back are different than the previous options, deal with that
        if (JSON.stringify(inputStates[name]?.options) !== JSON.stringify(options)) {
          const userInput = userInputs?.find(u => u.name === name);

          // choose which option to set as current value of this categorical input
          let newVal = inputStates[name].value;

          if (!newVal) {
            const areAnyNewOptionsReferencedInInputDefaults = userInput?.defaults?.some(d => {
              return options.map(o => JSON.stringify(o)).includes(d.value)
            })
            if (options.length === 1 || !areAnyNewOptionsReferencedInInputDefaults) {
              newVal = options[0];
            } else if (userInput?.defaults?.length) {
              for (const { conditionals: defaultConditionals, value } of userInput.defaults) {
                if (!defaultConditionals?.length) {
                  // there are no conditionals so set the first default value
                  newVal = JSON.parse(value);
                  break;
                } else if (
                    defaultConditionals.every((conditional) =>
                      checkConditionalOptimized(conditional, inputStates)
                    )
                ) {
                  newVal = value;
                  break;
                }
              }
            }
          }

          if (typeof newVal !== 'string') {
            newVal = String(newVal)
          }
      
          setInputStates((vals) => ({
            ...vals,
            [name]: { ...vals[name], options, value: newVal },
          }));
        }
      // }, { refetchOnWindowFocus: false, enabled: doAllPreviousCategoricalInputsHaveValues })
      }
      // return result;
    })  
  }, [sourceOrAnalysis, inputStates, requestCache])
  
  // Reset empty inputState if userInputs changes
  useEffect(() => {
    // compare the keys of the current inputState to an array of the user input names...
    // ...if the stringified arrays are different the userInputs have changed

    if (
      !isStructurallyEqual(
        Object.keys(inputStates),
        Object.keys(userInputsToState)
      )
    ) {
      setInputStates(userInputsToState);
    }
  }, [inputStates, userInputsToState]);

  // 1. Input visibility derived from conditionals
  // 2. Set defaults
  // 3. Input validation
  useEffect(() => {
    if (!userInputs) return;

    setInputStates(prevInputStates => {
      if (!userInputs) {
        return prevInputStates;
      }

      const currentInputStates = { ...prevInputStates };
      let currentStateUpdated = false;


      for (const {
        conditionals = [],
        validators = [],
        defaults = [],
        type,
        name,
        options,
      } of userInputs) {
        // check all input conditionals, an input is only visible if all conditionals pass
        const isVisible = conditionals.every((conditional) =>
          checkConditionalOptimized(conditional, currentInputStates)
        );
        if (isVisible !== currentInputStates[name]?.isVisible) {
          // here we set the visibility boolean and the value:
          // newValue is always an empty string: either we are unsetting it
          // when visibility goes from true > false, or the value is empty as
          // it hasn't been set yet when going from false > true
          currentInputStates[name] = {
            ...currentInputStates[name],
            isVisible,
            value: "",
          };
          currentStateUpdated = true;
        }

        // if categorical input has a value but no options
        // if (type === 'categorical'
        //   && currentInputStates[name]?.value
        //   && !currentInputStates[name]?.options
        // )

        // set option values to only those that pass conditional checks
        const optionValues = (options || [])
          .filter(({ conditionals: optionValuesConditionals = [] }) =>
            optionValuesConditionals.every((conditional) =>
              checkConditionalOptimized(conditional, currentInputStates)
            )
          )
          .map(({ value }) => value);

        if (
          options &&
          !isStructurallyEqual(optionValues, currentInputStates[name]?.options) 
        ) {
          let value = currentInputStates[name]?.value;
          if (value && value !== "" && optionValues.indexOf(value) === -1) {
            // selected option is no longer available
            value = "";
          }
          currentInputStates[name] = {
            ...currentInputStates[name],
            options: optionValues,
            value,
          };
          currentStateUpdated = true;
        }

        // set defaults only if a value is not already present
        if (
          (
            !currentInputStates[name]?.value ||
            currentInputStates[name]?.value === ""
          )
          &&
          !currentInputStates[name].isFocused
          &&
          !currentInputStates[name].wasJustManuallyCleared
        ) {
          if (defaults.length > 0) {
            for (const { conditionals: defaultConditionals, value } of defaults) {
              // since the API returns JSON as the default values,
              // we parse it here before setting it on the input by calling
              // e.g. JSON.parse('"NREL"') or JSON.parse('0.004')
              const newValue: number | string = JSON.parse(value);
              const roundedVal =
                typeof newValue === "string"
                  ? newValue
                  : roundToHundredth(newValue).toString();

              // Do not set default on a categorical input with no options
              if (
                type === 'categorical' &&
                (!currentInputStates[name]?.options ||
                  currentInputStates[name]?.options.length === 0)
              ) {
                break;
              }

              if (!defaultConditionals?.length) {
                // there are no conditionals so set the first default value
                if (
                  roundedVal !== currentInputStates[name]?.value &&
                  currentInputStates[name]?.isVisible &&
                  (currentInputStates[name]?.value === "" ||
                    currentInputStates[name]?.value === undefined)
                ) {
                  currentInputStates[name] = {
                    ...currentInputStates[name],
                    value: roundedVal,
                  };
                  currentStateUpdated = true;
                  break;
                }
              } else {
                if (
                  defaultConditionals.every((conditional) =>
                    checkConditionalOptimized(conditional, currentInputStates)
                  )
                ) {
                  if (currentInputStates[name]?.value !== roundedVal) {
                    currentInputStates[name] = {
                      ...currentInputStates[name],
                      value: roundedVal,
                    };
                    currentStateUpdated = true;
                    break;
                  }
                }
              }
            }
          } else {
            // If we get here, it means no defaults are specified in the metadata from backend.
            // For a good UX, if there's only one option available, choose it.
            if (currentInputStates[name]?.options?.length === 1) {
              const value = currentInputStates[name].options[0];
              currentInputStates[name] = {
                ...currentInputStates[name],
                value: value,
              };
              currentStateUpdated = true;
            } else if (isVisible && isInputBoolean(type, options)) {
              currentInputStates[name] = {
                ...currentInputStates[name],
                value: 'No'
              }
              currentStateUpdated = true;
            }
          }
        }

        const errors = [];
        const warnings = [];

        for (const { args, ...rest } of validators) {
          // break the loop if the input doesn't have a value yet
          // or if the value to be validated isn't a number
          // since, for now, we only validate numbers (floats|ints)
          if (
            !currentInputStates[name]?.value ||
            Number.isNaN(parseFloat(currentInputStates[name]?.value))
          ) {
            break;
          }

          const unparsedValue = currentInputStates[name]?.value;
          const value = (type === 'continuous' ? JSON.parse(JSON.stringify(Number(unparsedValue))) : JSON.parse(unparsedValue));

          let error;

          if (args.length === 0) {
            // `numeric` = float | int
            if (
              rest.name === "numeric" &&
              (Number.isNaN(parseFloat(value)) ||
                Number.isNaN(parseInt(value, 10)))
            ) {
              error = "Please enter an integer or a float";
            } else if (
              rest.name === "integer" &&
              Number.isNaN(parseInt(value, 10))
            ) {
              error = "Please enter an integer";
            }
          } else {
            // logical operators: lt, gt, lte, gte
            // https://github.mit.edu/sesame/sesame-core/blob/develop/core/validators.py
            const [numericVal] = args;
            switch (rest.name) {
              case "gte":
                if (value < numericVal)
                  error = `Please enter a value greater than or equal to ${numericVal}`;
                break;
              case "gt":
                if (value <= numericVal)
                  error = `Please enter a value greater than ${numericVal}`;
                break;
              case "lte":
                if (value > numericVal)
                  error = `Please enter a value less than or equal to ${numericVal}`;
                break;
              case "lt":
                if (value >= numericVal)
                  error = `Please enter a value less than ${numericVal}`;
                break;
              default:
                Sentry.captureEvent({
                  message: `Unexpected validator - name: ${rest.name}, value: ${numericVal}`,
                });
            }
          }

          if (error) {
            if (rest.warning) {
              warnings.push(rest.message || error);
            } else {
              errors.push(rest.message || error);
            }
          }
        }

        const error = errors.join(", ");
        if (error !== currentInputStates[name]?.error && error.length > 0) {
          currentInputStates[name] = { ...currentInputStates[name], error };
          currentStateUpdated = true;
        }

        const warning = warnings.join(", ");
        if (warning !== currentInputStates[name]?.warning && warning.length > 0) {
          currentInputStates[name] = { ...currentInputStates[name], warning };
          currentStateUpdated = true;
        }

        // if (currentStateUpdated) {
        //   setInputStates(currentInputStates);
        // }
      }

      if (currentStateUpdated) {
        return currentInputStates;
      } else {
        return prevInputStates;
      }

    })

  }, [checkConditionalOptimized, inputStates, userInputs]);



  // useEffect hook that fetches categorical input options:
  // 1. if it's the first input and it's categorical with no options, fetch options
  // 2. if it's categorical and the input before it has a value, fetch options

  // useEffect(() => {
  //   async function fetchOptions(name: string, index?: number) {

  //     const categoricalIndexOfThisInput = categoricalInputStateKeys.indexOf(name);

  //     const categoricalInputKeysBeforeThisOne = categoricalInputStateKeys.slice(0, categoricalIndexOfThisInput)

  //     const doAllPreviousCategoricalInputsHaveValues = categoricalInputKeysBeforeThisOne
  //       .filter(key => inputStates[key].isVisible)
  //       .every(key => inputStates[key].value)
      
  //     // console.log(name, categoricalIndexOfThisInput, categoricalInputKeysBeforeThisOne.map(key => inputStates[key].value), doAllPreviousCategoricalInputsHaveValues)
  //     // console.log('this value:', inputStates[name].value)
  //     // don't fetch options from server if previous visible categorical inputs don't have their own values set yet
  //     if (categoricalIndexOfThisInput > 0 && !doAllPreviousCategoricalInputsHaveValues) {
  //       console.log('skipping, not all previous values set yet')
  //       return;
  //     }

  //     console.log('fetching...')
  //     const queryParams = categoricalInputStateKeys
  //       .filter(key => inputStates[key].isVisible && inputStates[key].value && key !== name)
  //       .map(key => `${key}=${encodeURIComponent(inputStates[key].value)}`)
  //       .join('&')

  //     let url = `${path}`;
  //     if (sourceOrAnalysis) {
  //       url += `/${sourceOrAnalysis}`;
  //     }
  //     url += `/user_inputs/${name}`;

  //     const request = `${url}${
  //       queryParams !== "" ? `?${queryParams}` : ""
  //     }`;

  //     // const { data, status } = await useQuery("categoricalOptions", client(request))

  //     // const { data, status } = useQuery(['categoricalOptions', request], async () => {
  //     //   const data = await client(request)
  //     //   return data
  //     // })

  //     const data = await client(request);

  //     if (!Array.isArray(data?.options)) return;
  //     const options: string[] = data?.options || [];

  //     // if the options we just got back are different than the previous options, deal with that
  //     if (JSON.stringify(inputStates[name]?.options) !== JSON.stringify(options)) {
  //       const userInput = userInputs?.find(u => u.name === name);

  //       // choose which option to set as current value of this categorical input
  //       let newVal = inputStates[name].value;

  //       if (!newVal) {
  //         const areAnyNewOptionsReferencedInInputDefaults = userInput?.defaults?.some(d => {
  //           return options.map(o => JSON.stringify(o)).includes(d.value)
  //         })
  //         if (options.length === 1 || !areAnyNewOptionsReferencedInInputDefaults) {
  //           newVal = options[0];
  //         } else if (userInput?.defaults?.length) {
  //           for (const { conditionals: defaultConditionals, value } of userInput.defaults) {
  //             if (!defaultConditionals?.length) {
  //               // there are no conditionals so set the first default value
  //               newVal = JSON.parse(value);
  //               break;
  //             } else if (
  //                 defaultConditionals.every((conditional) =>
  //                   checkConditionalOptimized(conditional, inputStates)
  //                 )
  //             ) {
  //               newVal = value;
  //               break;
  //             }
  //           }
  //         }
  //       }

  //       if (typeof newVal !== 'string') {
  //         newVal = String(newVal)
  //       }
        
  //       setInputStates((vals) => ({
  //         ...vals,
  //         [name]: { ...vals[name], options, value: newVal },
  //       }));
  //     }
  //   }

  //   for (let i = 0; i < inputStateKeys.length; i++) {
  //     const name = inputStateKeys[i];
  //     const isCategorical = userInputs?.find(
  //       (u) => u.name === name
  //     )?.type === 'categorical';
  //     let prevItemIdx = i - 1;
  //     let prevVisibleInput = inputStates[inputStateKeys[prevItemIdx]];

  //     // we can't naively take the previous userInput since it may not be visible
  //     // ... so we have to walk backward and find the first visible input to see
  //     // ... if it has a value
  //     if (i >= 1) {
  //       while (!prevVisibleInput.isVisible) {
  //         prevItemIdx--;
  //         prevVisibleInput = inputStates[inputStateKeys[prevItemIdx]];
  //       }
  //     }

  //     if (
  //       i === 0 &&
  //       isCategorical &&
  //       (!inputStates[name].options || inputStates[name].options.length === 0)
  //     ) {        
  //       fetchOptions(name);
  //       break;
  //     }

  //     if (
  //       i >= 1 &&
  //       isCategorical &&
  //       prevVisibleInput?.value &&
  //       prevVisibleInput?.value !== "" &&
  //       inputStates[name].isVisible &&
  //       (!inputStates[name].options || inputStates[name].options.length === 0)
  //     ) {
  //       fetchOptions(name, i);
  //       break;
  //     }
  //   }
  // }, [categoricalInputStates, sourceOrAnalysis, path, client]);

  const isValid = React.useMemo(() => {
    let valid = userInputs ? true : false;
    for (const key of Object.keys(inputStates)) {
      const input = inputStates[key];
      if (input.isVisible && (!!input.error || input.value === "")) {
        valid = false;
      }
    }
    return valid;
  }, [inputStates, userInputs]);

  // 1. If the user is changing a non-categorical input and the set of subsequent user inputs
  // ... includes a categorical input, we should clear all subsequent existing values
  // ... since they may not make sense any longer
  // 2. When changing a categorical selection, only the subsequent categorical inputs
  // ... would need to be cleared

  const setNewInputState = (name: string, value: string, opts?: SetInputOptions) => {

    // change to functional mode of state setting, to avoid situation where relatively concurrent input state updates w/shareTable were overwriting each other because of setState's async/batch behavior
    setInputStates(prevState => {
      let isPrecedingCategorical = false;
      const userInput = userInputs?.find((u) => u.name === name);
      // avoid octal JSON.parse error if someone enters e.g. "05" in an input - this converts "05" or "005" to "5", or "00.5" to "0.5", but leaves "0.5" intact
      if (userInput?.type === 'continuous') {
        if (value.length > 1) {
          value = value.replace(/^0+(?!\.)/, '');
        }
      }
      // value = userInput?.type === 'continuous' ? String(Number(value)) : value;

      const isCategorical = userInput?.type === 'categorical';
      const hasOptions = userInput?.options;
      const currentIndex = inputStateKeys.indexOf(name);
      const clonedInputStates = JSON.parse(JSON.stringify(prevState));

      for (let i = currentIndex + 1; i < inputStateKeys.length; i++) {
        const inputName = inputStateKeys[i];
        if (
          userInputs
            ?.filter((u) => clonedInputStates[u.name].isVisible)
            .find((u) => u.name === inputName)?.type === 'categorical'
        ) {
          isPrecedingCategorical = true;
        }
      }

      // TODO: uncomment when the API accepts a hash of named properties
      // and does not rely on order of query params to infer input type
      if ((isCategorical || hasOptions) && isPrecedingCategorical) {
        // clear subsequent categorical inputs
        for (let i = currentIndex + 1; i < inputStateKeys.length; i++) {
          const inputName = inputStateKeys[i];
          if (
            userInputs
              ?.filter((u) => clonedInputStates[u.name].isVisible)
              .find((u) => u.name === inputName)?.type === 'categorical'
          ) {
            clonedInputStates[inputName] = {
              ...clonedInputStates[inputName],
              value: "",
              error: "",
              options: [],
            };
          }
        }
      }

      if (isPrecedingCategorical) {
        // otherwise clear all inputs
        clonedInputStates[name] = {
          ...clonedInputStates[name],
          value: "",
          error: "",
          options: [],
        };
      }

      // clear inputs that depend on this one so their defaults can be recalculated
      const inputsWhoseDefaultsDependOnThisInput = userInputs?.filter(input => {
        return input.defaults?.some(defawlt => {
          return defawlt.conditionals.some(conditional => {
            return conditional.args[0] === name // check that conditional input name equals name of input that was just changed
          })
        })
      });
      inputsWhoseDefaultsDependOnThisInput?.forEach(input => {
        clonedInputStates[input.name] = { ...clonedInputStates[input.name], value: "", error: "" };
      });

      clonedInputStates[name] = { ...clonedInputStates[name], value, error: "" };
      if (typeof opts?.isFocused !== 'undefined') {
        clonedInputStates[name].isFocused = opts.isFocused;
      }
      if (typeof opts?.wasJustManuallyCleared !== 'undefined') {
        clonedInputStates[name].wasJustManuallyCleared = opts.wasJustManuallyCleared;
      }
      return clonedInputStates;
    });
  };

  const setError = (inputName: string, error: string) => {
    setInputStates((vals) => ({
      ...vals,
      [inputName]: { ...vals[inputName], error },
    }));
  };

  return [inputStates, setNewInputState, isValid, setSourceOrAnalysis, userInputs, setError];
};

export default useUserInputs;

export const getInputValuesRecordFromInputStates = (inputStates: Record<string, InputState>): Record<string, string> => {
  return Object.keys(inputStates).reduce((acc, cur) => {
    acc[cur] = inputStates[cur].value;
    return acc;
  }, {} as Record<string, string>)
}

const isInputBoolean = (type: string, options: Option[] | undefined) => {
  const optionValues = options?.map(o => o.value);
  return options?.length === 2 && optionValues?.includes('Yes') && optionValues?.includes('No')
}