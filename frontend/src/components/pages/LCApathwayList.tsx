import * as React from "react";
import { Link, navigate } from "gatsby";
import { Transition } from "@headlessui/react";
import { format } from "date-fns";
import { v4 as uuidv4 } from "uuid";
import tw from "twin.macro";
import styled from "@emotion/styled";
import * as Styles from "../styles";

import useLocalStorage from "../../hooks/useLocalStorage";
import useOutsideClick from "../../hooks/useOutsideClick";
import Layout from "../layout";

export const Button = styled.button<{
  disabled?: boolean;
  variant?: "red" | "blue";
}>`
  ${({ disabled }) => (disabled ? tw`opacity-50 cursor-not-allowed` : "")}
  ${tw`transition-all ml-4 my-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-base font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2`};
  ${({ variant }) =>
    variant === "red"
      ? tw`bg-red-600 hover:bg-red-700 focus:ring-red-500`
      : tw`bg-blue-600 hover:bg-blue-700 focus:ring-blue-500`}
`;

const Pathways = ({ pathname }: { pathname: string }): JSX.Element => {
  const ref = React.useRef(null);
  const [pathways, setPathways] = useLocalStorage<
    Record<string, SinglePathway>
  >("pathways", {});
  const [currentPathway, setCurrentPathway] = React.useState("");
  const [selectedPathways, setSelectedPathways] = React.useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = React.useState("");
  const [selectedType, setSelectedType] = React.useState<null | string>(null);

  useOutsideClick([ref], () => {
    if (currentPathway !== "") {
      setCurrentPathway("");
    }
  });

  return (
    <Layout pathname={pathname} hideRibbon={true} className="py-0">
      <div className="">
        <div className="flex">
          <h1 className="non-comparison-cell text-2xl flex items-center font-semibold">
            Saved Pathways - Emissions (LCA)
          </h1>
          <span className="order-1 sm:order-1 shadow-sm rounded-md ml-auto mr-6">
            <Button
              onClick={() =>
                navigate(
                  `/app/emissions?pathways=${selectedPathways.join(",")}`
                )
              }
              disabled={
                selectedPathways.length === 0 || selectedType === "in-progress"
              }
              type="button"
              variant="blue"
            >
              <svg
                className="-ml-1 mr-3 h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Analyze
            </Button>
            <Button
              type="button"
              variant="red"
              disabled={selectedPathways.length === 0}
              onClick={() => {
                const clonePathways = JSON.parse(JSON.stringify(pathways));
                for (const key of selectedPathways) {
                  delete clonePathways[key];
                }
                navigate(`?p=${selectedPathways[0]}`);
                setPathways(clonePathways);
              }}
            >
              <svg
                className="-ml-1 mr-3 h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </Button>
          </span>
        </div>

        <div className="align-middle inline-block min-w-full border-b border-gray-200">
          <table className="min-w-full">
            <thead>
              <tr className="border-t border-gray-200">
                <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  <span className="lg:pl-2">Completed</span>
                </th>
                <th className="hidden md:table-cell px-8 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  Last updated
                </th>
                <th className="hidden md:table-cell px-6 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  Select
                </th>
                <th className="pr-6 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {Object.keys(pathways).filter(
                (key) => pathways[key]?.userJson["5"]?.isComplete
              ).length === 0 ? (
                <tr>
                  <td className="px-6 py-3 max-w-0 w-full whitespace-no-wrap leading-5 font-medium text-gray-900">
                    You have no completed pathways
                  </td>
                </tr>
              ) : null}
              {Object.keys(pathways)
                .sort((a, b) => {
                  const categoryA =
                    pathways[a]?.userJson["0"].category ||
                    pathways[a]?.userJson[
                      Object.keys(pathways[a]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;
                  const categoryB =
                    pathways[b]?.userJson["0"].category ||
                    pathways[b]?.userJson[
                      Object.keys(pathways[b]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;
                  if (!categoryA || !categoryB) return 0;
                  if (categoryA < categoryB) return -1;
                  if (categoryB < categoryA) return 1;
                  return 0;
                })
                .map((key) => {
                  if (!pathways[key]?.userJson["5"]?.isComplete) return null;
                  const category =
                    pathways[key]?.userJson["0"].category ||
                    pathways[key]?.userJson[
                      Object.keys(pathways[key]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;
                  const disabled =
                    selectedType === "completed" && selectedCategory !== ""
                      ? selectedCategory !== category
                      : selectedType === "in-progress";
                  return (
                    <tr key={key}>
                      <td className="relative px-6 py-3 max-w-0 w-full whitespace-no-wrap leading-5 font-medium text-gray-900">
                        <div
                          className={`transition-all absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <div className="flex items-center space-x-3 lg:pl-2">
                          <Styles.CategoryBadge
                            category={category || "No category"}
                          >
                            {category || "No category"}
                          </Styles.CategoryBadge>
                          <a href="#" className="truncate hover:text-gray-600">
                            <span>{pathways[key].pathwayName} </span>
                          </a>
                        </div>
                      </td>

                      <td className="relative hidden md:table-cell px-6 py-3 whitespace-no-wrap leading-5 text-gray-500 text-right">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        {format(
                          new Date(pathways[key].lastUpdated),
                          "MMM dd hh:mm aaa"
                        )}
                      </td>
                      <td className="relative hidden md:table-cell px-6 py-3 whitespace-no-wrap leading-5 text-gray-500 text-right">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <input
                          disabled={disabled}
                          checked={selectedPathways.includes(key)}
                          onChange={() => {
                            if (selectedPathways.includes(key)) {
                              setSelectedPathways(
                                selectedPathways.filter((p) => p !== key)
                              );
                              if (
                                selectedPathways.filter((p) => p !== key)
                                  .length === 0
                              ) {
                                setSelectedType(null);
                                setSelectedCategory("");
                              }
                            } else {
                              setSelectedType("completed");
                              setSelectedPathways([...selectedPathways, key]);
                              if (category) {
                                setSelectedCategory(category);
                              }
                            }
                          }}
                          type="checkbox"
                        />
                      </td>
                      <td className="pr-6 relative">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <div className="relative flex justify-end items-center">
                          <button
                            id="project-options-menu-0"
                            aria-haspopup="true"
                            type="button"
                            onClick={() => {
                              if (disabled) return;
                              setCurrentPathway(
                                currentPathway === key ? "" : key
                              );
                            }}
                            className="w-8 h-8 inline-flex items-center justify-center text-gray-400 rounded-full bg-transparent hover:text-gray-500 focus:outline-none focus:text-gray-500 focus:bg-gray-100 transition ease-in-out duration-150"
                          >
                            {/* <!-- Heroicon name: dots-vertical --> */}
                            <svg
                              className="w-5 h-5"
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                            </svg>
                          </button>

                          <div className="relative">
                            <Transition
                              show={currentPathway === key}
                              enter="transition ease-out duration-100"
                              enterFrom="transform opacity-0 scale-95"
                              enterTo="transform opacity-100 scale-100"
                              leave="transition ease-in duration-75"
                              leaveFrom="transform opacity-100 scale-100"
                              leaveTo="transform opacity-0 scale-95"
                              className="z-10 origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-200"
                            >
                              <div className="py-1" ref={ref}>
                                <Link
                                  to={`/app?pid=${key}`}
                                  className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                  role="menuitem"
                                >
                                  <svg
                                    className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
                                    <path
                                      fillRule="evenodd"
                                      d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                  Edit
                                </Link>
                                <a
                                  href="#"
                                  onClick={() => {
                                    const p = pathways[key];
                                    const parensRegex = /\(.*\)/;

                                    // tally the number of pathways with the same name,
                                    // ignoring the "(copy ${int})" from the ends of the strings
                                    const numPathways = Object.entries(
                                      pathways
                                    ).filter(
                                      ([k]) =>
                                        pathways[k].pathwayName
                                          .replace(parensRegex, "")
                                          .trim() ===
                                        p.pathwayName
                                          .replace(parensRegex, "")
                                          .trim()
                                    ).length;

                                    const pathwayName =
                                      numPathways > 1
                                        ? // remove string between parens, e.g. "(copy 1)"
                                          `${p.pathwayName.replace(
                                            parensRegex,
                                            ""
                                          )} (copy ${parseInt(
                                            `${numPathways}` || "0"
                                          )})`
                                        : `${p.pathwayName} (copy 1)`;

                                    const clonedPathway = JSON.parse(
                                      JSON.stringify({ ...p, pathwayName })
                                    );

                                    setPathways({
                                      ...pathways,
                                      [uuidv4()]: clonedPathway,
                                    });
                                  }}
                                  className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                  role="menuitem"
                                >
                                  <svg
                                    className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path d="M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z" />
                                    <path d="M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h8a2 2 0 00-2-2H5z" />
                                  </svg>
                                  Duplicate
                                </a>
                                <a
                                  href="#"
                                  onClick={() =>
                                    navigate(`/app/emissions?pathways=${key}`)
                                  }
                                  className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                  role="menuitem"
                                >
                                  <svg
                                    className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                                    />
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                  </svg>
                                  Analyze
                                </a>
                              </div>
                              <div className="border-t border-gray-100"></div>
                              <div className="py-1">
                                <Link
                                  onClick={() => {
                                    const clonePathways = JSON.parse(
                                      JSON.stringify(pathways)
                                    );
                                    delete clonePathways[key];
                                    setPathways(clonePathways);
                                  }}
                                  to={`?p=${key}`}
                                  className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                  role="menuitem"
                                >
                                  {/* <!-- Heroicon name: trash --> */}
                                  <svg
                                    className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                  Delete
                                </Link>
                              </div>
                            </Transition>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
        <div className="align-middle inline-block min-w-full border-b border-gray-200">
          <table className="min-w-full">
            <thead>
              <tr className="border-t border-gray-200">
                <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  <span className="lg:pl-2">In Progress</span>
                </th>
                <th className="hidden md:table-cell px-8 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  Last updated
                </th>
                <th className="hidden md:table-cell px-6 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider">
                  Select
                </th>
                <th className="pr-6 py-3 border-b border-gray-200 bg-gray-50 text-right text-sm leading-4 font-medium text-gray-500 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {Object.keys(pathways).filter(
                (key) => !pathways[key]?.userJson["5"]?.isComplete
              ).length === 0 ? (
                <tr>
                  <td className="px-6 py-3 max-w-0 w-full whitespace-no-wrap leading-5 font-medium text-gray-900">
                    You have no in progress pathways
                  </td>
                </tr>
              ) : null}
              {Object.keys(pathways)
                .sort((a, b) => {
                  const categoryA =
                    pathways[a]?.userJson["0"].category ||
                    pathways[a]?.userJson[
                      Object.keys(pathways[a]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;
                  const categoryB =
                    pathways[b]?.userJson["0"].category ||
                    pathways[b]?.userJson[
                      Object.keys(pathways[b]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;
                  if (!categoryA || !categoryB) return 0;
                  if (categoryA < categoryB) return -1;
                  if (categoryB < categoryA) return 1;
                  return 0;
                })
                .map((key) => {
                  if (pathways[key]?.userJson["5"]?.isComplete) return null;
                  const category =
                    pathways[key]?.userJson["0"].category ||
                    pathways[key]?.userJson[
                      Object.keys(pathways[key]?.userJson).length - 1
                    ]?.activityOptions[0]?.category;

                  const disabled = selectedType === "completed";

                  return (
                    <tr key={key}>
                      <td className="relative px-6 py-3 max-w-0 w-full whitespace-no-wrap leading-5 font-medium text-gray-900">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <div className="flex items-center space-x-3 lg:pl-2">
                          <Styles.CategoryBadge
                            category={category || "No category"}
                          >
                            {category || "No category"}
                          </Styles.CategoryBadge>
                          <a href="#" className="truncate hover:text-gray-600">
                            <span>{pathways[key].pathwayName} </span>
                          </a>
                        </div>
                      </td>

                      <td className="relative hidden md:table-cell px-6 py-3 whitespace-no-wrap text-gray-400 text-right">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        {format(
                          new Date(pathways[key].lastUpdated),
                          "MMM dd hh:mm aaa"
                        )}
                      </td>
                      <td className="relative hidden md:table-cell px-6 py-3 whitespace-no-wrap leading-5 text-gray-500 text-right">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <input
                          disabled={selectedType === "completed"}
                          checked={selectedPathways.includes(key)}
                          onChange={() => {
                            if (selectedPathways.includes(key)) {
                              setSelectedPathways(
                                selectedPathways.filter((p) => p !== key)
                              );
                              if (
                                selectedPathways.filter((p) => p !== key)
                                  .length === 0
                              ) {
                                setSelectedType(null);
                                setSelectedCategory("");
                              }
                            } else {
                              setSelectedPathways([...selectedPathways, key]);
                              setSelectedType("in-progress");
                              if (category) {
                                setSelectedCategory(category);
                              }
                            }
                          }}
                          type="checkbox"
                        />
                      </td>
                      <td className="relative pr-6">
                        <div
                          className={`transition-all pointer-events-none absolute h-full w-full inset-0 z-5 ${
                            disabled
                              ? "bg-gray-200 opacity-75 cursor-not-allowed"
                              : ""
                          }`}
                        ></div>
                        <div className="relative flex justify-end items-center">
                          <button
                            id="project-options-menu-0"
                            aria-haspopup="true"
                            type="button"
                            onClick={() => {
                              if (disabled) return;
                              setCurrentPathway(
                                currentPathway === key ? "" : key
                              );
                            }}
                            className="w-8 h-8 inline-flex items-center justify-center text-gray-400 rounded-full bg-transparent hover:text-gray-500 focus:outline-none focus:text-gray-500 focus:bg-gray-100 transition ease-in-out duration-150"
                          >
                            <svg
                              className="w-5 h-5"
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                            </svg>
                          </button>
                          <div className="relative">
                            <Transition
                              show={currentPathway === key}
                              enter="transition ease-out duration-100"
                              enterFrom="transform opacity-0 scale-95"
                              enterTo="transform opacity-100 scale-100"
                              leave="transition ease-in duration-75"
                              leaveFrom="transform opacity-100 scale-100"
                              leaveTo="transform opacity-0 scale-95"
                              className="z-10 origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-200"
                            >
                              <div
                                className="z-10 rounded-md bg-white shadow-xs"
                                role="menu"
                                aria-orientation="vertical"
                                aria-labelledby="project-options-menu-0"
                              >
                                <div className="py-1">
                                  <Link
                                    to={`/app?pid=${key}`}
                                    className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                    role="menuitem"
                                  >
                                    <svg
                                      className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                      xmlns="http://www.w3.org/2000/svg"
                                      viewBox="0 0 20 20"
                                      fill="currentColor"
                                    >
                                      <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
                                      <path
                                        fillRule="evenodd"
                                        d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
                                        clipRule="evenodd"
                                      />
                                    </svg>
                                    Edit
                                  </Link>
                                </div>
                                <div className="border-t border-gray-100"></div>
                                <div className="py-1">
                                  <Link
                                    onClick={() => {
                                      const clonePathways = JSON.parse(
                                        JSON.stringify(pathways)
                                      );
                                      delete clonePathways[key];
                                      setPathways(clonePathways);
                                    }}
                                    to={`#${key}`}
                                    className="group flex items-center px-4 py-2 leading-5 text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900"
                                    role="menuitem"
                                  >
                                    {/* <!-- Heroicon name: trash --> */}
                                    <svg
                                      className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-500"
                                      xmlns="http://www.w3.org/2000/svg"
                                      viewBox="0 0 20 20"
                                      fill="currentColor"
                                    >
                                      <path
                                        fillRule="evenodd"
                                        d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                        clipRule="evenodd"
                                      />
                                    </svg>
                                    Delete
                                  </Link>
                                </div>
                              </div>
                            </Transition>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
};

export default Pathways;
