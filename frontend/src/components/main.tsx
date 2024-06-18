import React from "react";
import { PageProps } from "gatsby";
import Header from "./header";
import Footer from "./footer";
import { Global } from "@emotion/react";
import { css } from "twin.macro";
import { colors, white, black } from "../utils/constants";
import { MainWithoutHeader } from "./layout";

const Main: React.FunctionComponent<PageProps> = ({
  children,
  location: { pathname },
}) => {
  const isDashboard = pathname.includes("covid");
  return (
    <>
      <Global
        styles={css`
          body {
            transition: background-color 0.3s
              cubic-bezier(0.46, 0.03, 0.52, 0.96);
            background-color: ${isDashboard ? colors.gray["900"] : "none"};
          }

          .site-title {
            transition: color 0.3s cubic-bezier(0.46, 0.03, 0.52, 0.96);
            color: ${isDashboard ? white : "none"};
          }

          .header-link {
            transition: color 0.3s cubic-bezier(0.46, 0.03, 0.52, 0.96);
            color: ${isDashboard ? colors.gray["200"] : "none"};
            &:focus {
              color: ${isDashboard ? white : "none"};
            }
            &:hover {
              color: ${isDashboard ? white : "none"};
            }
          }

          .mobile-header-link {
            color: ${isDashboard ? colors.gray["200"] : colors.gray["900"]};
            &:hover {
              background-color: ${isDashboard
                ? colors.gray["700"]
                : colors.gray["200"]};
              color: ${isDashboard ? white : black};
            }
          }

          .highcharts-credits {
            margin-top: 5rem;
            font-size: 0.85rem !important;
            fill: ${colors.gray["700"]} !important;
          }

          .header-logo {
            filter: ${isDashboard
              ? "invert(50%) sepia(13%) saturate(200%) hue-rotate(130deg) brightness(200%) contrast(80%)"
              : "none"};
          }
        `}
      />
      <Header />
      <MainWithoutHeader>{children}</MainWithoutHeader>
      <Footer />
    </>
  );
};

export default Main;
