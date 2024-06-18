import {
  useMemo,
  useState,
  useCallback,
  Dispatch,
  SetStateAction,
} from "react";
import client from "../utils/client";
import useLocalStorage from "./useLocalStorage";

type UseAuth = {
  token: string;
  logout: () => void;
  loading: boolean;
  errors: string | undefined;
  setErrors: Dispatch<SetStateAction<string | undefined>>;
  authenticate: (email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
};

const useAuth = (): UseAuth => {
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useLocalStorage("authToken", "");
  const [errors, setErrors] = useState<string | undefined>();

  const authenticate = useCallback(
    async (email: string, password: string) => {
      const body = { email, password };

      try {
        setLoading(true);
        setErrors(undefined);
        const res = await client("/auth/login", { body });
        setLoading(false);

        if (res.token && typeof res.token === "string") {
          setToken(res.token);
        }
      } catch (res) {
        setLoading(false);
        if (res.errors) {
          setErrors(res.errors);
        }
      }
    },
    [setToken]
  );

  const logout = useCallback(() => {
    setToken("");
  }, [setToken]);

  const isAuthenticated = useMemo(() => token !== "", [token]);

  return {
    token,
    logout,
    loading,
    errors,
    setErrors,
    authenticate,
    isAuthenticated,
  };
};

export default useAuth;
