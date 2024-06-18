import React, { useReducer, useContext } from "react";
import { useStaticQuery, graphql, Link } from "gatsby";
import { Transition } from "@headlessui/react";
import { Global } from "@emotion/react";
import tw, { css } from "twin.macro";
import { GatsbyImage } from "gatsby-plugin-image";
import { Column } from "./column";
import { AppHeader } from "./appHeader";
import styled from "@emotion/styled";
import * as Styles from "./styles"
import isPropValid from "@emotion/is-prop-valid";
import useAuth from "../hooks/useAuth";
import useLocalStorage from "../hooks/useLocalStorage";
import { ModuleStateContext } from "./comparableResultsModule";
import '../css/layout.css'
import { Toaster } from "react-hot-toast";
import { triggerResize } from "../utils";
import { useAtomValue } from "jotai";
import { isAnyModalOpenAtom } from "./pages/dashboard";
import { externalFeedbackFormUrl, FeedbackWidget } from "./feedbackWidget"

export const NavLink = styled(Link, {
  shouldForwardProp: (prop: string | number | symbol) => isPropValid(prop),
})<{ isActive: boolean, isDark: boolean }>`
  ${tw`flex items-center px-2 py-3 h-10 text-base leading-5 font-medium focus:outline-none transition ease-in-out duration-150`}
  ${({ isDark }) => isDark ? tw`text-gray-300 hover:text-gray-100 hover:bg-gray-700 focus:bg-gray-50` : tw`text-gray-600 hover:text-gray-900 hover:bg-gray-50 focus:bg-gray-50`}
  ${({ isActive, isDark }) => isActive && !isDark && tw`bg-white text-black font-bold`}
  ${({ isActive, isDark }) => isActive && isDark && tw`bg-gray-900 text-white`}
`;

export const MainWithoutHeader: React.FunctionComponent = ({ children }) => {
  return <main>{children}</main>;
};

function useHover() {
  const [value, setValue] = React.useState(false);
  const ref = React.useRef(null);
  const handleMouseOver = (e) => {
    e.stopPropagation();
    setValue(true);
  }
  const handleMouseOut = (e) => {
    e.stopPropagation();
    setValue(false);
  }
  React.useEffect(
    () => {
      const node = ref.current;
      if (node) {
        node.addEventListener("mouseover", handleMouseOver);
        node.addEventListener("mouseout", handleMouseOut);
        return () => {
          node.removeEventListener("mouseover", handleMouseOver);
          node.removeEventListener("mouseout", handleMouseOut);
        };
      }
    },
    [ref.current] // Recall only if ref changes
  );
  return [ref, value];
}

type LayoutProps = {
  type?: 'page' | 'app';
  pathname?: string;
  secondCol?: JSX.Element[];// Array<AnalysisResultToDisplayProps>;
  handleRun?: () => Promise<void>;
  handleSave?: () => Promise<void>;
  inputHandlerRefs?: React.MutableRefObject<React.ReactElement>[];
  isRunButtonDisabled?: boolean;
  isSaveButtonDisabled?: boolean;
  isLoading?: boolean;
  title?: string;
  hideRibbon?: boolean;
  showColumnDisplayButtons?: boolean;
  padResults?: boolean;
  resultsRibbonContent?: JSX.Element;
  appHeaderContent?: JSX.Element;
  contentWrapperClasses?: string;
}

const Layout: React.FunctionComponent<LayoutProps> = ({
  type = 'app',
  children,
  pathname,
  secondCol,
  title,
  hideRibbon,
  handleRun,
  handleSave,
  inputHandlerRefs,
  isRunButtonDisabled,
  isSaveButtonDisabled,
  isLoading,
  showColumnDisplayButtons = true,
  padResults,
  resultsRibbonContent,
  appHeaderContent,
  contentWrapperClasses = '',
}) => {

  pathname = pathname || location.pathname;

  const moduleState = React.useContext(ModuleStateContext)

  const {isComparisonMode} = React.useContext(ModuleStateContext)

  const isModalOpen = useAtomValue(isAnyModalOpenAtom)

  // const renderCount = React.useRef(0);

  const data = useStaticQuery(graphql`
    query HeaderQuery {
      MITEIFull: file(relativePath: { eq: "MITEIFull.png" }) {
        childImageSharp {
          gatsbyImageData(height: 60, placeholder: NONE, layout: CONSTRAINED)
        }
      }
    }
  `);

  const [pathways] = useLocalStorage<Record<string, SinglePathway>>(
    "pathways",
    {}
  );
  const [TEAPathways] = useLocalStorage<
    Record<
      string,
      Record<
        string,
        {
          inputs: Record<string, InputState>;
          indicator: string;
          userInputs: UserInputProperties[];
        }
      >
    >
  >("TEA_pathways", {});

  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const { logout } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true)
  const [wasSidebarSetOpen, setWasSidebarSetOpen] = React.useState(true) // tracks whether user manually set sidebar open or closed

  const toggleSidebar = () => {
    // console.log('toggling sidebar, but before that, wasSidebarSetOpen:', wasSidebarSetOpen);
    const currentSidebarWasSetOpen = wasSidebarSetOpen;
    setWasSidebarSetOpen(!currentSidebarWasSetOpen);
    setIsSidebarOpen(!isSidebarOpen)
    triggerResize()
    // setIsSidebarOpenWithNewSidebarAndFullscreenState(!currentSidebarWasSetOpen, moduleState.isAnyColumnFullscreened);
  }

  const setIsSidebarOpenWithNewSidebarAndFullscreenState = (newWasSidebarSetOpen: boolean, newFullscreenState: boolean) => {
    let shouldSetSidebarOpen = true;
    if (newWasSidebarSetOpen) {
      shouldSetSidebarOpen = true;
    }
    if (newFullscreenState || !newWasSidebarSetOpen) {
      shouldSetSidebarOpen = false;
    }
    // console.log('setting sidebar open with new fullscreen state, wasSidebarSetOpen:', wasSidebarSetOpen, ' newFullscreenState:', newFullscreenState);
    setIsSidebarOpen(shouldSetSidebarOpen);
  }

  React.useEffect(() => {
    // if (moduleState.isAnyColumnFullscreened) {
    if (moduleState.isComparisonMode) {
      setIsSidebarOpen(true)
      setWasSidebarSetOpen(true)
    } else {
      setIsSidebarOpenWithNewSidebarAndFullscreenState(wasSidebarSetOpen, moduleState.isAnyColumnFullscreened as boolean);
    }
    // setIsSidebarOpen
  }, [moduleState.isAnyColumnFullscreened])

  React.useEffect(() => {
    if (moduleState.isComparisonMode) {
      setIsSidebarOpen(false);
      // setWas
    } else {
      setIsSidebarOpen(true);
    }
  }, [moduleState.isComparisonMode])



  // console.log(moduleState.comparisonResultIds)

  interface SidebarCategoryIconProps {
    colorClass?: string;
    fill?: string;
    stroke?: string;
    viewBox?: string;
  }

  const SidebarCategoryIcon: React.FC<SidebarCategoryIconProps> = ({
    children,
    colorClass = 'text-gray-200',
    stroke = "currentColor",
    fill = "none",
    viewBox = "0 0 24 24",
  }) => {
    return (
      <svg
        className={`mr-3 ${!isSidebarOpen ? 'h-8 w-8 ml-1' : 'h-6 w-6 ml-[1px]'} ${colorClass} flex-shrink-0`}
        xmlns="http://www.w3.org/2000/svg"
        fill={fill}
        viewBox={viewBox}
        stroke={stroke}
      >
        {children}
      </svg>
    )
  }

  interface NavGroupProps {
    title: string,
    titleClass: string,
    wrapperClasses?: string;
    titleUrl?: string,
    icon: React.ReactNode,
    items?: {
      title: string,
      href: string,
      counter?: string,
    }[]
  }

  const NavGroup: React.FC<NavGroupProps> = ({
    title,
    titleClass = null,
    wrapperClasses,
    titleUrl,
    icon,
    items,
  }) => {

    const [hoverRef, isHovered] = useHover();

    // const overrideIsHovered = true;

    const navGroupHeader = (
      <>
        {icon}
        <span className={`${!isSidebarOpen ? 'ml-5' : ''}`}>{title}</span>
      </>
    )

    const headerClasses = [
      `z-10 transition-all`,
      `${isSidebarOpen ? 'w-full' : 'cursor-pointer overflow-hidden'}`,
      `${!isSidebarOpen && isHovered ? 'w-[14rem] rounded-tr shadow-lg' : ''}`,
      `${!isSidebarOpen && !isHovered ? 'w-16' : ''}`,
      `px-3 group w-full flex items-center py-2 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${titleClass}`,
    ].join(' ');

    const isLinkExternal = !!titleUrl?.match(/http|www/gi)?.length

    return (
      <div ref={hoverRef} className={`relative z-30 ${isSidebarOpen ? 'h-auto' : 'z-10 h-12'} ${!isSidebarOpen && !isHovered ? 'overflow-hidden' : '' } ${wrapperClasses ?? ''}`}>
        {titleUrl
          ?
          (isLinkExternal
            ?
            <a href={titleUrl} target="_blank" className={headerClasses}>
              {navGroupHeader}
            </a>
            :
            <Link to={titleUrl || ''} className={headerClasses}>
              {navGroupHeader}
            </Link>
          )
          
          :
          <div className={headerClasses}>
            {navGroupHeader}
          </div>
        }

        {items &&
          <>
            {isSidebarOpen ?

              <div className=''>
                {items.map((item, index) => {
                  const isActive = pathname === item.href;
                  return (
                    <NavLink
                      isDark={false}
                      to={item.href}
                      isActive={isActive}
                      className="group h-10"
                      key={index}
                    >
                      <div className="pl-2">{item.title}</div>
                      {/* {isActive ? <div className="absolute right-4 text-lg text-gray-600">›</div> : ''} */}
                    </NavLink>
                  )
                })}
              </div>

              :

              <>
                <div className={`transition-all ${isHovered ? 'w-40 opacity-100' : 'w-0 opacity-0'} z-10 shadow-lg rounded-b bg-gray-800 absolute top-12 left-16`}>
                  {items.map((item, index) => {
                    const isActive = pathname === item.href;
                    return (
                      <NavLink
                        isDark={true}
                        to={item.href}
                        isActive={isActive}
                        className="group overflow-x-visible whitespace-nowrap active:!bg-gray-800"
                        key={index}
                      >
                        <div className="pl-2">{item.title}</div>
                        {/* {isActive ? <div className="absolute right-4 text-white">›</div> : ''} */}
                      </NavLink>
                    )
                  })}
                </div>
              </>
            }
          </>
        }
      </div>
    )
  }

  return (
    <>
      {/* <div className="py-1 px-2 bg-red-500 text-white">Layout rendered {(renderCount.current ++)} time(s)</div> */}

      <Global
        styles={css`
          body {
            ${tw`bg-gray-50`}
          }
        `}
      />

      <div><Toaster
        toastOptions={{
          style: {
            borderRadius: '5px',
            border: '1px solid #e5e7eb',
          },
          success: {
            iconTheme: {
              primary: '#60a218',
              secondary: 'white',
            }
            // style: {
            //   background: 'green',
            // },
          },
          // error: {
          //   style: {
          //     background: 'red',
          //   },
          // },
        }}
      /></div>

      <div className={`h-screen flex lg:overflow-hidden bg-white`} style={isModalOpen ? {filter: 'blur(4px)'} : {}}>
          
        <FeedbackWidget />


        {/* <!-- Off-canvas menu for mobile, show/hide based on off-canvas menu moduleState. --> */}
        <div className="lg:hidden">
          <div
            className={`fixed inset-0 flex z-40 ${
              mobileMenuOpen ? "block" : "hidden"
            }`}
          >
            <Transition
              show={mobileMenuOpen}
              enter="transition-opacity ease-linear duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="transition-opacity ease-linear duration-300"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div
                className="fixed inset-0"
                onClick={() => setMobileMenuOpen(false)}
              >
                <div className="absolute inset-0 bg-gray-600 opacity-75"></div>
              </div>
            </Transition>
            {/* Off-canvas menu, show/hide based on off-canvas menu state */}
            {/* MOBILE MENU */}
            <Transition
              show={mobileMenuOpen}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <div
                className="relative flex flex-1 flex-col max-w-xs w-full pt-5 pb-4 bg-white"
                style={{ minHeight: "100vh" }}
              >
                <div className="absolute top-0 right-0 -mr-14 p-1">
                  <button
                    className="flex items-center justify-center h-12 w-12 rounded-full focus:outline-none focus:bg-gray-600"
                    aria-label="Close sidebar"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  >
                    <svg
                      className="h-6 w-6 text-white"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
                <div className="flex-shrink-0 flex items-center px-4">
                  <GatsbyImage
                    alt="MIT Energy Initiative Logo"
                    image={data.MITEIFull.childImageSharp.gatsbyImageData}
                    className="h-auto w-32"
                  />
                </div>
                <div className="mt-5 flex-1 h-0 overflow-y-auto">
                  <nav className="px-2">
                    <div className="space-y-1">
                      <Link
                        to="/app/cars"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Cars
                      </Link>

                      <Link
                        to="/app/power"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Power
                      </Link>

                      {/* <Link to="/app/power-historic" className="">
                        <svg
                          className="mr-3 h-6 w-6 text-gray-400 group-hover:text-gray-500 group-focus:text-gray-600 transition ease-in-out duration-150"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        Power Historic
                      </Link> */}
                      <Link
                        to="/app/power-greenfield"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Power Greenfield
                      </Link>

                      <Link
                        to="/app/build"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Build
                      </Link>

                      {/* <Link
                        to="/app/emissions"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Emissions (LCA)
                      </Link> */}

                      <Link
                        to="/app/costs"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Costs (TEA)
                      </Link>

                      {/* <Link
                        to="/app/pathways/emissions"
                        className="group flex items-center px-2 py-2 text-base leading-5 font-medium rounded-md text-gray-900 bg-gray-100 hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-200 focus:outline-none transition ease-in-out duration-150"
                      >
                        Saved pathways
                      </Link> */}
                    </div>
                  </nav>
                </div>
              </div>
            </Transition>
            {/* END OF MOBILE MENU */}

            <div className="flex-shrink-0 w-14">
              {/* <!-- Dummy element to force sidebar to shrink to fit close icon --> */}
            </div>
          </div>
        </div>

        {/* <!-- Sidebar nav for desktop --> */}
        <div id="sidebar" className={`hidden lg:flex lg:flex-shrink-0 relative ${isSidebarOpen ? 'w-44' : 'w-16 overflow-x-visible'} ${moduleState.isAnyColumnFullscreened ? 'z-30' : ''}`}>
          
          <div className="w-full flex flex-col bg-gray-100">
            <div className="flex items-center flex-shrink-0 gutter-x h-12 text-2xl text-gray-700 font-bold">
              <svg xmlns="http://www.w3.org/2000/svg" onClick={toggleSidebar} style={{right: '1.1rem'}} className={`z-10 cursor-pointer hover:text-gray-800 transition-colors absolute top-3 h-6 w-6 text-gray-500 ${moduleState.isAnyColumnFullscreened ? 'hidden' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isSidebarOpen ?
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                :
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                }
              </svg>
              {isSidebarOpen &&
                <Link to="/app" className="relative" style={{lineHeight: 1}}>SESAME<div className="text-green-600 opacity-70 text-sm text-right -mt-1">BETA</div></Link>
              }
            </div>
            {/* <!-- Sidebar component, swap this element with another sidebar if you like --> */}
            <div className={`h-0 flex-1 flex flex-col ${isSidebarOpen ? 'overflow-y-auto' : ''}`}>
              {/* <!-- Navigation --> */}
              <nav className="flex flex-col h-full">

                {/* <NavGroup
                  title="Dashboard"
                  titleClass="text-stone-200 bg-gradient-to-r from-stone-600 to-stone-800"
                  titleUrl="/app/dashboard"
                  icon={
                    <SidebarCategoryIcon viewBox="0 0 20 20" fill="currentColor" stroke="2">
                      <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                    </SidebarCategoryIcon>
                  }
                /> */}

                <NavGroup
                  title="Systems"
                  titleClass="text-white text-gray-100 bg-gradient-to-r from-blue-700 to-purple-700"
                  icon={
                    <SidebarCategoryIcon colorClass="text-gray-300">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
                      />
                    </SidebarCategoryIcon>
                  }
                  items={[
                    { title: 'Cars', href: '/app/cars' },
                    { title: 'Power', href: '/app/power' },
                    // { title: 'Power Historic', href: '/app/power-historic' },
                    { title: 'Power Greenfield', href: '/app/power-greenfield' },
                    { title: 'Industrial Fleet', href: '/app/industrial-fleet' },
                  ]}
                />

                <NavGroup
                  title="Paths"
                  titleClass="text-white bg-gradient-to-r from-yellow-500 to-red-500"
                  icon={
                    <SidebarCategoryIcon>
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4.871 4A17.926 17.926 0 003 12c0 2.874.673 5.59 1.871 8m14.13 0a17.926 17.926 0 001.87-8c0-2.874-.673-5.59-1.87-8M9 9h1.246a1 1 0 01.961.725l1.586 5.55a1 1 0 00.961.725H15m1-7h-.08a2 2 0 00-1.519.698L9.6 15.302A2 2 0 018.08 16H8"
                      />
                    </SidebarCategoryIcon>
                  }
                  items={[
                    { title: 'Build', href: "/app/build" },
                    { title: 'Costs (TEA)', href: "/app/costs" },
                    { title: 'Industry', href: '/app/industry' },
                  ]}
                />

                <NavGroup
                  title="Saved"
                  titleClass="text-white bg-gradient-to-r from-lime-600 to-emerald-600"
                  titleUrl="/app/saved"
                  icon={
                    <SidebarCategoryIcon>
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                      />
                    </SidebarCategoryIcon>
                  }
                />

                <NavGroup
                  title="Settings"
                  titleClass="text-stone-100 bg-gradient-to-r from-stone-500 to-stone-700"
                  titleUrl="/app/settings"
                  icon={
                    <SidebarCategoryIcon>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </SidebarCategoryIcon>
                  }
                />

                <div className={`mt-auto ${!isSidebarOpen ? 'h-60' : ''}`}>
                  <NavGroup
                    title="Feedback"
                    wrapperClasses="mt-auto border-b"
                    titleClass="bg-white text-gray-600 border-t mt-auto"
                    titleUrl={externalFeedbackFormUrl}
                    icon={
                      <SidebarCategoryIcon
                        fill="currentColor"
                        stroke="none"
                        viewBox="0 0 20 20"
                        colorClass="text-gray-600"
                      >
                        <path fillRule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clipRule="evenodd" />
                      </SidebarCategoryIcon>
                    }
                  />                 
                  <NavGroup
                    title="Help"
                    wrapperClasses="mt-auto border-b"
                    titleClass="bg-white text-gray-600 mt-auto"//"bg-gradient-to-r from-gray-600 to-gray-900"
                    titleUrl="/app/help"
                    icon={
                      <SidebarCategoryIcon
                        fill="currentColor"
                        stroke="none"
                        viewBox="0 0 20 20"
                        colorClass="text-blue-500"
                      >
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </SidebarCategoryIcon>
                    }
                  />

                  {!isSidebarOpen &&
                    <div className="flex items-center flex-shrink-0 gutter-x text-2xl text-gray-700 font-bold transform rotate-90 mt-4">
                      <Link to="/app" className="relative" style={{lineHeight: 1}}>SESAME<div className="text-green-600 opacity-70 text-sm text-right -mt-1">BETA</div></Link>
                    </div>
                  }
                </div>



                    {/* <div className="space-y-0">
                      <NavLink
                        to="/app/pathways/emissions"
                        isActive={pathname.includes("/app/pathways/emissions")}
                        className="group"
                      >
                        <div className="pl-10">Emissions (LCA)</div>
                        {Object.keys(pathways).filter(
                          (key) => pathways[key]?.userJson["5"]?.isComplete
                        ).length > 0 && (
                          <span className="bg-blue-100 group-hover:bg-blue-200 ml-auto inline-block py-0.5 px-3 text-xs font-medium rounded-full">
                            {
                              Object.keys(pathways).filter(
                                (key) =>
                                  pathways[key]?.userJson["5"]?.isComplete
                              ).length
                            }
                          </span>
                        )}
                      </NavLink>

                      <NavLink
                        to="/app/pathways/costs"
                        isActive={pathname.includes("/app/pathways/costs")}
                        className="group"
                      >
                        <div className="pl-10">Costs (TEA)</div>
                        {Object.keys(TEAPathways).length > 0 && (
                          <span className="bg-blue-100 group-hover:bg-blue-200 inline-block py-0.5 px-3 ml-2 text-xs font-medium rounded-full">
                            {Object.keys(TEAPathways).length}
                          </span>
                        )}
                      </NavLink>
                    </div> */}
              </nav>
            </div>
            {isSidebarOpen &&
              <div className="flex-shrink-0 gutter-x py-4">
                <div className="flex-shrink-0 w-full group block">
                  <div className="mb-6">
                    {
                      [
                        {
                          text: 'About',
                          to: '/#about'
                        },
                        {
                          text: 'Team',
                          to: '/#team'
                        },
                        // {
                        //   text: 'COVID-19 Dashboard',
                        //   to: '/covid'
                        // }
                      ].map((linkItem, index) => {
                        return (
                          <div className="py-1" key={index}>
                            <Link
                              className="block text-sm text-gray-600 hover:text-gray-800"
                              to={linkItem.to}
                            >
                              {linkItem.text}
                            </Link>
                          </div>
                        )
                      })
                    }
                    <div className="mt-4">
                      <Link
                        className="hover:text-black inline-flex items-center px-3 py-2 border border-gray-500 shadow-sm text-sm leading-4 rounded-md text-gray-600  hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        onClick={() => logout()}
                        to="/"
                      >
                        Log Out
                      </Link>
                    </div>
                  </div>
                  <div className="">
                    <div className="mt-4 text-xs text-gray-600">
                      © {new Date().getFullYear()} MITEI
                    </div>
                  </div>
                </div>
              </div>
            }
          </div>
        </div>

        {/* <!-- Main column --> */}

        <div className={`flex flex-col w-0 flex-1 lg:overflow-hidden ${moduleState.isAnyColumnFullscreened ? 'z-20' : ''}`}>

          <div className="relative z-10 flex-shrink-0 flex h-16 bg-white border-b border-gray-300 lg:hidden">
            {/* <!-- Sidebar toggle, controls the 'sidebarOpen' sidebar moduleState. --> */}
            <button
              className={`w-16 text-center border-r border-gray-300 text-gray-500 focus:outline-none focus:bg-gray-100 focus:text-gray-600 lg:hidden`}
              aria-label="Open sidebar"
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen);
              }}
            >
              <svg
                className="h-6 w-6 mx-auto"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M4 6h16M4 12h8m-8 6h16" />
              </svg>
            </button>
            <div className="flex items-center flex-shrink-0 gutter-x text-2xl text-gray-700 font-bold">
              <Link to="/app">SESAME</Link>
            </div>
            <div className="flex-shrink-0 flex items-center px-4 absolute right-0 top-0">
              <GatsbyImage
                alt="MIT Energy Initiative Logo"
                image={data.MITEIFull.childImageSharp.gatsbyImageData}
                className="h-auto w-24 mt-1"
              />
            </div>
          </div>

          <div id="columns-wrapper" className={`flex-1 flex flex-col relative z-0 border-l border-gray-300 h-screen overflow-y-auto  ${contentWrapperClasses}`}>
            <div className={`flex flex-col flex-1 ${!isComparisonMode && type !== 'page' ? 'h-screen' : ''}`}>
              {type === 'page' && 
                <div className={`px-6 pt-5 pb-6`}>
                  <Styles.H2>{title}</Styles.H2>
                  {children}
                </div>
              }
              {type === 'app' &&
                <>
                  <AppHeader extraContent={appHeaderContent} />
                  <div className={`flex-auto flex flex-col ${moduleState.isComparisonMode ? '' : 'lg:flex-row lg:overflow-hidden'} `}>

                    {type === 'app' &&
                      <>
                        <Column
                          tabIndex={0}
                          title={title}
                          handleRun={handleRun}
                          handleSave={handleSave}
                          inputHandlerRefs={inputHandlerRefs}
                          isRunButtonDisabled={isRunButtonDisabled}
                          isSaveButtonDisabled={isSaveButtonDisabled}
                          isLoading={isLoading}
                          hideRibbon={hideRibbon}
                          type="inputs"
                          showColumnDisplayButtons={showColumnDisplayButtons}
                        >
                          {children}
                        </Column>

                        {secondCol ? (
                          <>
                            <Column
                              // style={{ zIndex: -1 }}
                              // title={`${getHeaderTitle(pathname)}: Results`}
                              type="results"
                              ribbonContent={resultsRibbonContent}
                              showColumnDisplayButtons={showColumnDisplayButtons}
                              // className="relative xl:flex xl:flex-col flex-shrink-0 w-7/12 overflow-x-auto"
                            >
                              <div className={padResults ? 'non-comparison-cell' : ''}>
                                {secondCol}
                              </div>
                            </Column>
                            {/* {moduleState.comparisonResultIds.map((id, index) => {
                              return (
                                <Column
                                  type="results"
                                  comparisonResultId={id}
                                  comparisonIndex={index}
                                  showColumnDisplayButtons={showColumnDisplayButtons}
                                >
                                </Column>
                              )
                            })} */}
                            {/* <div className="w-12"></div> */}
                          </>
                        ) : null}
                      </>
                    }
                  
                  </div>
                </>
              }
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Layout;
