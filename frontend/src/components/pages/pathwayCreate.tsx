import React, { useEffect, useMemo, useReducer } from "react";
import { navigate, Link } from "gatsby";
import { RouteComponentProps } from "@reach/router";
// import { motion, AnimatePresence } from "framer-motion";
import { v4 as uuidv4 } from "uuid";
import useQueryString from "use-query-string";

import { reducer, initialState } from "../pathwayCreatorState";
import * as Styles from "../styles";
import Layout from "../layout";
import Modal from "../modal";
import useUserInputs from "../../hooks/useUserInputs";
import useLocalStorage from "../../hooks/useLocalStorage";
import useAppMetadata from "../../hooks/useAppMetadata";
import usePreviousValue from "../../hooks/usePreviousValue";
import {
  CategorySelect,
  PathwayNameInput,
  SourceSelect,
  ActivitySelect,
  DirectionPicker,
} from "../appSelects";
import SEO from "../seo";
import UserInputs from "../userInputs";
import { capitalStr } from "../../utils";

const IndexPage = ({
  pathname,
  location,
}: {
  pathname: string;
  location: RouteComponentProps["location"];
}): JSX.Element => {
  const [query]: [Record<string, unknown>] = useQueryString(location, navigate);

  const {
    allStage: { edges: allStageNodes },
    allLink: { edges: allLinkNodes },
  } = useAppMetadata();
  const [
    {
      pathwayId,
      startsWith,
      stageId,
      activityId,
      category,
      sourceId,
      pathwayName,
      userJson,
      mode,
      showModal,
      lastSetBy,
    },
    dispatch,
  ] = useReducer(
    reducer,
    initialState(
      // either generate a new uuid or take it from the query string if
      // we're editing
      query.pid && typeof query.pid === "string" ? query.pid : uuidv4()
    )
  );

  const [pathways, setPathways] = useLocalStorage<
    Record<string, SinglePathway>
  >("pathways", {});

  useEffect(() => {
    // on page load, if one of the pathways is missing a `lastSavedAt` date,
    // or was created before the timestamp `1622132560812` (2021/05/21 circa 12:00pm)
    if (
      Object.keys(pathways).some(
        (key) =>
          !pathways[key].lastUpdated ||
          pathways[key].lastUpdated < 1622132560812
      )
    ) {
      setPathways({});
    }
  }, [pathways, setPathways]);

  const allStages = useMemo(() => {
    if (
      startsWith === "enduse" &&
      allStageNodes[0].node.name.toLowerCase() === "enduse"
    ) {
      return [...allStageNodes];
    } else {
      return [...allStageNodes.reverse()];
    }
  }, [startsWith, allStageNodes]);

  useEffect(() => {
    if (query.pid && typeof query.pid === "string" && mode !== "edit") {
      const edit: Mode = "edit";
      dispatch({ type: "setMode", mode: edit });

      const p = pathways[query.pid];
      const pathwayUserJson = p.userJson;

      dispatch({ type: "setPathwayName", value: p.pathwayName });

      if (!p.userJson["0"]?.activity.includes("enduse")) {
        dispatch({ type: "setStartsWithEdit", stage: "upstream" });
      }
      dispatch({ type: "setSelectionAndInputs", json: pathwayUserJson });
      dispatch({ type: "setStageFromBreadcrumb", index: 5 });
    }
  }, [query.pid, pathways, allStages, mode]);

  const activity = useMemo(
    () =>
      allStages[stageId]?.node.activities.find(({ id }) => id === activityId),
    [activityId, allStages, stageId]
  );

  const activityOptions = useMemo(() => {
    if (stageId === 0) {
      if (startsWith === "enduse" && category) {
        return allStages[stageId].node.activities.filter(
          (a) => a.category === category
        );
      }
      return allStages[stageId].node.activities;
    } else {
      let prevActivityLinks = undefined;
      let i = stageId;
      while (!prevActivityLinks) {
        i = i - 1;
        prevActivityLinks = userJson[parseInt(Object.keys(userJson)[i])]?.links;
      }

      const nextActivities =
        startsWith === "enduse"
          ? prevActivityLinks.reduce(
              (acc: string[], cur) => [...acc, cur.node.end],
              []
            )
          : prevActivityLinks.reduce(
              (acc: string[], cur) => [...acc, cur.node.start],
              []
            );
      const opts = allStages[stageId]?.node.activities.filter((a) =>
        nextActivities.includes(a.id)
      );
      return opts;
    }
  }, [stageId, allStages, userJson, startsWith, category]);

  // skip stage if there are no activity options
  useEffect(() => {
    if (!activityOptions?.length) {
      dispatch({ type: "skipStage", index: stageId });
    }
  }, [activityOptions, stageId]);

  const source = useMemo(
    () => activity?.sources.find(({ id }) => id === sourceId),
    [activity, sourceId]
  );

  const [inputs, setInput, isValid, setSourceOrAnalysis, flattenedUserInputs, setInputError] = useUserInputs(
    source?.user_inputs,
    sourceId,
    undefined,
    undefined,
    { 'compute_cost': false },
  );

  const prevCategory = usePreviousValue(category);
  // if the category changes, wipe out the userInputMetadata
  useEffect(() => {
    if (prevCategory !== category) {
      dispatch({ type: "setActivityId", id: undefined });
      dispatch({
        type: "setUserInputMetadata",
        userInputs: [],
        index: stageId,
      });
    }
  }, [category, stageId, source, prevCategory]);

  useEffect(() => {
    if (!userJson[stageId]) return;
    const { userInput, ...rest } = userJson[stageId];

    // if user inputs have changed, it saves the inputs to userJson
    if (JSON.stringify(userInput) === JSON.stringify(inputs)) return;
    const newUserJson = {
      ...userJson,
      [stageId]: {
        ...rest,
        category,
        activityOptions,
        userInputMetadata: source?.user_inputs,
        userInput: inputs,
        isComplete: stageId === 5 && isValid,
      },
    };
    dispatch({
      type: "setSelectionAndInputs",
      json: newUserJson,
    });
    if (source?.user_inputs.length === 0) {
      dispatch({ type: "setNextStage" });
    }

    if (
      pathways[pathwayId] &&
      JSON.stringify(newUserJson) ===
        JSON.stringify(pathways[pathwayId].userJson)
    )
      return;

    setPathways({
      ...pathways,
      [pathwayId]: {
        ...pathways[pathwayId],
        lastUpdated: Date.now(),
        pathwayName,
        userJson: newUserJson,
      },
    });
  }, [
    pathwayName,
    isValid,
    source,
    stageId,
    userJson,
    inputs,
    pathwayId,
    pathways,
    setPathways,
    category,
    activityOptions,
  ]);

  useEffect(() => {
    const currentStage = userJson[stageId];
    if (currentStage?.activity) return;
    if (activityOptions?.length > 1) return;
    if (!activityOptions) return;
    const value = activityOptions[0]?.id;
    if (value) {
      dispatch({ type: "setActivityId", id: value });
      dispatch({ type: "setSourceId", id: undefined });
      dispatch({
        type: "setSelectionAndInputs",
        json: {
          ...userJson,
          [stageId]: {
            activity: value,
            links:
              startsWith === "enduse"
                ? allLinkNodes.filter(({ node: { start } }) => value === start)
                : allLinkNodes.filter(({ node: { end } }) => value === end),
          },
        },
      });
    }
  }, [userJson, stageId, activityOptions, allLinkNodes, startsWith]);

  useEffect(() => {
    // if there is only one source for the chosen activity,
    // automatically select it
    const firstActivitySourceId = activity?.sources[0].id;
    if (userJson[stageId]?.source === firstActivitySourceId) return;
    if (activity?.sources?.length === 1) {
      if (!userJson[stageId]) {
        return;
      }
      dispatch({ type: "setSourceId", id: firstActivitySourceId });
      const { userInput, ...rest } = userJson[stageId];
      dispatch({
        type: "setSelectionAndInputs",
        json: {
          ...userJson,
          [stageId]: {
            ...rest,
            source: firstActivitySourceId,
          },
        },
      });
    }
  }, [activity, userJson, stageId]);

  const selectDataSource = (sourceId: string) => {
    const { userInput, ...rest } = userJson[stageId];
    dispatch({
      type: "setSelectionAndInputs",
      json: {
        ...userJson,
        [stageId]: {
          ...rest,
          source: sourceId,
        },
      },
    });
    dispatch({ type: "setSourceId", id: sourceId });
  };

  useEffect(() => {
    if (activity) {
      const source = activity.sources[0]; // use 1st source by default
      if (source) {
        selectDataSource(source.id);
      }
    }
  }, [activity]);

  return (
    <Layout pathname={pathname} showColumnDisplayButtons={false}>
      <div className="max-w-3xl non-comparison-cell">
        <div className="pb-12 col-span-1 lg:col-span-2">
          <SEO title="Pathway Analysis" />

          <>
            <div
              className="grid grid-cols-1 gap-1 lg:grid-cols-2 mb-2"
              style={{ alignItems: "end" }}
            >
              <div className="mb-4">
                <PathwayNameInput
                  pathwayName={pathwayName}
                  setPathwayName={(value) => {
                    dispatch({ type: "setTitleLastSetBy", actor: "user" });
                    dispatch({ type: "setPathwayName", value });
                  }}
                />
              </div>
              {/* general ui controls */}
              <div className="mb-4 ml-auto">
                <DirectionPicker
                  startsWith={startsWith as AnalysisDirection}
                  setStartsWith={(stage) =>
                    dispatch({ type: "setStartsWith", stage })
                  }
                />
              </div>
            </div>

            {/* <AnimatePresence> */}
              {allStages.map(({ node: { name } }, idx) => {
                if (
                  (idx !== stageId && Object.keys(userJson).length === 0) ||
                  (Object.keys(userJson).length > 0 &&
                    !Object.keys(userJson).includes(`${idx}`)) ||
                  userJson[idx]?.activityOptions?.length === 0 ||
                  idx > stageId ||
                  userJson[idx]?.skip
                  // userJson[idx]?.isComplete
                  // (stageId > 0 && !userJson[idx]?.links) ||
                  // (stageId > 0 && userJson[idx]?.links?.length === 0)
                  // (stageId > 0 && !userJson[idx]?.userInput) ||
                  // userJson[idx]?.userInputMetadata?.length === 0
                ) {
                  return null;
                } else {
                  const stageActivity = userJson[idx]?.activityOptions?.find(
                    (i) => i.id === userJson[idx]?.activity
                  );
                  const stageSource = stageActivity?.sources?.find(
                    (a) => a.id === userJson[idx]?.source
                  );
                  return (
                    <div //<motion.div
                      // initial={{ opacity: 0 }}
                      // animate={{ opacity: 1 }}
                      // exit={{ opacity: 0 }}
                      className={`animate-fade-in relative bg-gray-100 rounded pt-5 px-6 pb-4 mb-6`}
                      key={name}
                      onClick={() => {
                        if (idx >= stageId) {
                          return;
                        }
                        dispatch({
                          type: "setStageFromBreadcrumb",
                          index: idx,
                        });
                      }}
                    >
                      {idx < stageId ? (
                        <div
                          className={`absolute h-full w-full inset-0 z-[5] rounded-md ${
                            idx < stageId
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                      ) : null}

                      {/* {if (idx < stageId) && (<PastStage stageId={idx} />) } */}
                      <div className="font-bold text-lg text-gray-700 mb-4">
                        {name === "GateToEnduse"
                          ? "Gate to Enduse"
                          : capitalStr(name)}
                      </div>
                      <div className="grid grid-cols-2 lg:grid-cols-3 gap-x-4 gap-y-2 items-end">
                        {stageId === idx && (
                          <>
                            {startsWith === "enduse" && idx === 0 ? (
                              <CategorySelect
                                category={category || ""}
                                categories={allStages[0].node.categories}
                                onChange={(newCategory: string) => {
                                  dispatch({
                                    type: "setCategory",
                                    category: newCategory,
                                  });
                                  const pathwaysOfSameCatgory = Object.values(
                                    pathways
                                  )?.filter(
                                    (p) =>
                                      p.userJson["0"].category === newCategory
                                  );

                                  let title = `${newCategory} Pathway`;

                                  title += ` ${
                                    pathwaysOfSameCatgory?.length + 1
                                  }`;

                                  if (
                                    lastSetBy === "app" ||
                                    pathwayName === ""
                                  ) {
                                    dispatch({
                                      type: "setTitleLastSetBy",
                                      actor: "app",
                                    });
                                    dispatch({
                                      type: "setPathwayName",
                                      value: title,
                                    });
                                  }
                                }}
                              />
                            ) : null}
                            {(startsWith === "enduse" &&
                              category &&
                              activityOptions?.length > 1) ||
                            (startsWith !== "enduse" &&
                              activityOptions?.length > 1) ? (
                              <ActivitySelect
                                disabled={startsWith === "enduse" && !category}
                                activityId={activityId || ""}
                                activities={activityOptions}
                                onChange={(value: string) => {
                                  const currentActivity = activityOptions.find(
                                    ({ id }) => id === value
                                  );

                                  const pathwaysOfSameActivity = Object.values(
                                    pathways
                                  )?.filter((p) =>
                                    p.pathwayName.includes(
                                      currentActivity?.name || ""
                                    )
                                  );

                                  let title = `${
                                    currentActivity?.name || ""
                                  } Pathway`;

                                  title += ` ${
                                    pathwaysOfSameActivity?.length + 1
                                  }`;

                                  if (
                                    lastSetBy === "app" ||
                                    pathwayName === ""
                                  ) {
                                    dispatch({
                                      type: "setTitleLastSetBy",
                                      actor: "app",
                                    });
                                    dispatch({
                                      type: "setPathwayName",
                                      value: title,
                                    });
                                  }

                                  // always reset the source and user inputs
                                  // TODO: remove future options from all options
                                  dispatch({
                                    type: "setSourceId",
                                    id: undefined,
                                  });
                                  dispatch({
                                    type: "setActivityId",
                                    id: value,
                                  });
                                  dispatch({
                                    type: "setSelectionAndInputs",
                                    json: {
                                      ...userJson,
                                      [stageId]: {
                                        ...userJson[stageId],
                                        activity: value,
                                        links: (startsWith === "enduse"
                                          ? allLinkNodes.filter(
                                              ({ node: { start } }) =>
                                                value === start
                                            )
                                          : allLinkNodes.filter(
                                              ({ node: { end } }) =>
                                                value === end
                                            )) || {
                                          start: "",
                                          end: "",
                                          id: "",
                                        },
                                      },
                                    },
                                  });
                                }}
                              />
                            ) : null}

                            {activity && activity.sources?.length > 1 ? (
                              <SourceSelect
                                sourceId={sourceId || ""}
                                sources={activity?.sources}
                                onChange={(newSourceId) => {
                                  selectDataSource(newSourceId);
                                }}
                              />
                            ) : null}
                            <UserInputs
                              userInputs={source?.user_inputs || []}
                              inputStates={inputs}
                              setInput={setInput}
                              setInputError={setInputError}
                              layout={"column"}
                              noWrapper={true}
                            />
                          </>
                        )}

                        {idx < stageId && (
                          <>
                            {startsWith === "enduse" && idx === 0 ? (
                              <CategorySelect
                                category={userJson[idx]?.category || ""}
                                categories={[userJson[idx]?.category]}
                              />
                            ) : null}

                            {(startsWith === "enduse" &&
                              userJson[idx]?.category &&
                              userJson[idx]?.activityOptions?.length > 1) ||
                            (startsWith !== "enduse" &&
                              userJson[idx]?.activityOptions?.length > 1) ? (
                              <ActivitySelect
                                disabled={startsWith === "enduse" && !category}
                                activityId={userJson[idx]?.activity || ""}
                                activities={userJson[idx]?.activityOptions}
                              />
                            ) : null}

                            {stageSource &&
                            userJson[idx]?.source &&
                            stageActivity?.sources?.length &&
                            stageActivity?.sources?.length > 1 ? (
                              <SourceSelect
                                sourceId={userJson[idx]?.source || ""}
                                sources={[stageSource]}
                              />
                            ) : null}
                            <UserInputs
                              userInputs={userJson[idx]?.userInputMetadata}
                              inputStates={userJson[idx]?.userInput}
                              setInputError={setInputError}
                              layout={"column"}
                              noWrapper={true}
                            />
                          </>
                        )}

                        
                      </div>

                      {idx >= stageId ? (
                        <Styles.Button
                          disabled={!isValid}
                          className="mt-4 mb-2"
                          onClick={() => {
                            if (!userJson[stageId].isComplete) {
                              dispatch({ type: "setNextStage" });
                            } else {
                              dispatch({ type: "showModal", isShown: true });
                            }
                          }}
                        >
                          {userJson[stageId]?.isComplete ? "Finish" : "Next"}
                        </Styles.Button>
                      ) : null}

                    </div> //</motion.div>
                  );
                }
              })}
            {/* </AnimatePresence> */}
          </>
        </div>
        <Modal
          showModal={showModal}
          title="Pathway created"
          message={
            <>
              Your pathway <b>{pathwayName}</b> was successfully created.
            </>
          }
        >
          <div className="mt-3 sm:mt-2">
            <span className="flex w-full rounded-md shadow-sm">
              <button
                onClick={() => navigate(`/app/emissions?pathways=${pathwayId}`)}
                type="button"
                className="inline-flex justify-center w-full rounded-md border border-transparent px-4 py-2 bg-blue-600 text-base leading-6 font-medium text-white shadow-sm hover:bg-blue-500 focus:outline-none focus:border-blue-700 focus:shadow-outline-blue transition ease-in-out duration-150"
              >
                Analyze pathway
              </button>
            </span>
          </div>
          <div className="mt-3 sm:mt-2">
            <span className="flex w-full rounded-md shadow-sm">
              <Link
                to="/app"
                type="button"
                onClick={() => dispatch({ type: "createNewPathway" })}
                className="inline-flex justify-center w-full rounded-md border border-transparent px-4 py-2 bg-green-600 text-base leading-6 font-medium text-white shadow-sm hover:bg-green-500 focus:outline-none focus:border-green-700 focus:shadow-outline-green transition ease-in-out duration-150"
              >
                Create new pathway
              </Link>
            </span>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};

export default IndexPage;
