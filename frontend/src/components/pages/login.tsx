import React from "react";
import { navigate } from "gatsby";
import { RouteComponentProps } from "@reach/router";
import useAuth from "../../hooks/useAuth";
import * as Styles from "../styles";

const ErrorIcon = () => (
  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
    <svg
      className="h-5 w-5 text-red-500"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
        clipRule="evenodd"
      />
    </svg>
  </div>
);

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const LoginScreen = (props: RouteComponentProps): JSX.Element => {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");

  const { isAuthenticated, authenticate, loading, errors, setErrors } =
    useAuth();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!username || !password) return;

    await authenticate(username, password);
  };

  if (isAuthenticated) {
    navigate(`/app/dashboard`);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl leading-9 font-extrabold text-gray-900">
          Sign in to SESAME
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form
            onSubmit={(event) => {
              handleSubmit(event);
            }}
          >
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium leading-5 text-gray-700"
              >
                Email
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <input
                  onChange={(e) => {
                    setUsername(e.target.value);
                    setErrors(undefined);
                  }}
                  value={username}
                  id="email"
                  type="email"
                  required
                  name="email"
                  className={
                    errors
                      ? "block w-full pr-10 border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm rounded-md"
                      : "appearance-none block w-full px-3 py-2 border border-gray-400 rounded-md placeholder-gray-400 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 transition duration-150 ease-in-out sm:text-sm sm:leading-5"
                  }
                  placeholder="you@example.com"
                  aria-invalid={errors ? "true" : "false"}
                  aria-describedby={errors ? "email-error" : ""}
                />
                {errors ? <ErrorIcon /> : null}
              </div>
            </div>

            <div className="mt-6">
              <label
                htmlFor="password"
                className="block text-sm font-medium leading-5 text-gray-700"
              >
                Password
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <input
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErrors(undefined);
                  }}
                  value={password}
                  id="password"
                  type="password"
                  placeholder="····"
                  className={
                    errors
                      ? "block w-full pr-10 border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm rounded-md"
                      : "appearance-none block w-full px-3 py-2 border border-gray-400 rounded-md placeholder-gray-400 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 transition duration-150 ease-in-out sm:text-sm sm:leading-5"
                  }
                  required
                  aria-invalid={errors ? "true" : "false"}
                  aria-describedby={errors ? "email-error" : ""}
                />
                {errors ? <ErrorIcon /> : null}
              </div>
            </div>

            <div className="mt-8">
              <span className="block w-full rounded-md shadow-sm">
                <Styles.Button
                  type="submit"
                  className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:border-blue-700 focus:shadow-outline-blue active:bg-blue-700 transition duration-150 ease-in-out"
                  disabled={loading}
                >
                  {loading ? "Signing in..." : "Sign in"}
                </Styles.Button>
              </span>
            </div>
            {errors ? (
              <p
                className={`mt-4 text-sm text-red-600 ${
                  errors ? "" : "invisible"
                }`}
                id="email-error"
              >
                The email and/or password you have submitted are incorrect.
                Please try again.
              </p>
            ) : null}
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
