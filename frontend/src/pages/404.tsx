import React from "react";
import { Link } from "gatsby";
import SEO from "../components/seo";
import { isBrowser } from "../utils";

const NotFoundPage = (): JSX.Element | null =>
  isBrowser() ? (
    <>
      <SEO title="404: Not found" />
      <div className="fixed bottom-0 inset-x-0 px-4 pb-6 sm:inset-0 sm:p-0 sm:flex sm:items-center sm:justify-center">
        <div
          className="bg-white rounded-lg px-4 pt-5 pb-4 overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full sm:p-6"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-headline"
        >
          <div>
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg
                className="h-6 w-6 text-red-600"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div className="mt-3 text-center sm:mt-5">
              <h3
                className="text-lg leading-6 font-medium text-gray-900"
                id="modal-headline"
              >
                Page not found
              </h3>
              <div className="mt-2">
                <p className="text-sm leading-5 text-gray-500">
                  <p>You just hit a route that doesn&#39;t exist.</p>
                </p>
              </div>
            </div>
          </div>
          <div className="mt-5 sm:mt-6">
            <span className="flex w-full rounded-md shadow-sm">
              <Link
                to="/"
                className="inline-flex justify-center w-full rounded-md border border-transparent px-4 py-2 bg-blue-600 text-base leading-6 font-medium text-white shadow-sm hover:bg-blue-500 focus:outline-none focus:border-blue-700 focus:shadow-outline-blue transition ease-in-out duration-150 sm:text-sm sm:leading-5"
              >
                Go back to the homepage
              </Link>
            </span>
          </div>
        </div>
      </div>
    </>
  ) : null;

export default NotFoundPage;
