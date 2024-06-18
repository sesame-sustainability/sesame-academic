/**
 * This client implementation returns a callback which automatically sends the user authentication token with every API call.
 */
import { useCallback } from "react";
import client, { Client } from "../utils/client";
import useAuth from "./useAuth";

const useClient = (): {
  client: (
    endpoint: string,
    { body, headers }?: Client
  ) => Promise<Record<string, unknown> | object | undefined>;
} => {
  const { isAuthenticated, token, logout } = useAuth();

  const httpClient = useCallback(
    async (endpoint: string, { body, headers = {}, method }: Client = {}) => {
      if (isAuthenticated) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      try {
        return await client(endpoint, { body, headers, method });
      } catch (res) {
        // TODO: it would be better to check for a 401 status code here
        // since "unauthorized" could also mean a permissions-like error
        // `client` does not currently expose the HTTP status
        if (res.errors === "unauthorized") {
          logout();
        } else {
          throw res;
        }
      }
    },
    [isAuthenticated, logout, token]
  );

  return {
    client: httpClient,
  };
};

export default useClient;
