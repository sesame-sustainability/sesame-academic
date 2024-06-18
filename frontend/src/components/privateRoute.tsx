import React from "react";
import { RouteComponentProps } from "@reach/router";
import { navigate } from "gatsby";
import { isBrowser } from "../utils";
import useAuth from "../hooks/useAuth";
import { useUserProfile } from "../hooks/useUserProfile";
import { useInitializeDB } from "../hooks/useDB";
import { Loader } from "./styles";

const PrivateRoute: React.FunctionComponent<
  { component: React.FunctionComponent, path: string, title?: string } & RouteComponentProps
> = ({ component: Component, location, ...rest }) => {
  const { isAuthenticated } = useAuth();

  const hasInitializedDB = useInitializeDB()

  const [userProfile, isUserProfileLoading] = useUserProfile()

  if (!isAuthenticated && location?.pathname !== `/app/login` && isBrowser()) {
    navigate("/app/login");
    return null;
  }

  React.useEffect(() => {
    if (isBrowser() && !isUserProfileLoading && !userProfile) {
      const isOnProfilePage = window.location.href.includes('/app/profile')
      if (!isOnProfilePage) {
        navigate("/app/profile");
      }
    }
  }, [isUserProfileLoading])

  if (!isBrowser()) return null;

  if (!hasInitializedDB) {
    return (
      <div className="h-screen w-screen flex items-center justify-center flex-col">
        <div className="fade-in text-gray-400 font-bold mt-6 mb-6">Loading demo content...</div>
        <Loader />
      </div>
    )
  }

  return isBrowser() ? <Component {...rest} /> : null;
};
export default PrivateRoute;