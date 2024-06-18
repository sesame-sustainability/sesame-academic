import React from "react";
import { triggerResize } from "../utils";
import { fontSize } from "../utils/constants";
import { ModuleStateContext } from "./comparableResultsModule";
import { motion } from "framer-motion"

const Accordion = ({
  title,
  children,
  defaultOpen = false,
  isOpen,
  setIsOpen,
  theme,
  indentContent,
  padContentTop = false,
  stickyHeader,
  stickyIndex,
  headerContent,
  headerContentWhenOpen,
  headerContentWhenClosed,
  headerLayout,
  headerClassName,
  wrapperClassName,
  titleClassName,
}: {
  title: string | JSX.Element;
  children: React.ReactNode;
  defaultOpen?: boolean;
  isOpen?: boolean;
  setIsOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  theme?: 'subtle' | 'no-background';
  indentContent?: boolean;
  padContentTop?: boolean;
  stickyHeader?: boolean;
  stickyIndex?: number;
  headerContent?: JSX.Element;
  headerContentWhenOpen?: React.ReactNode;
  headerContentWhenClosed?: JSX.Element;
  headerLayout?: 'comparisonRow';
  headerClassName?: string;
  wrapperClassName?: string;
  titleClassName?: string;
}) => {

  if (!isOpen && !setIsOpen) {
    [isOpen, setIsOpen] = React.useState(defaultOpen)
  }
  const { isComparisonMode, comparisonCases } = React.useContext(ModuleStateContext)

  const elementId = `accordion--${typeof title === 'string' ? title.toLowerCase().replace(/ /g, '-') : ''}`
  // const renderCount = React.useRef(0);

  const topOffsetPx = (isComparisonMode ? (24/4) + (stickyIndex || 0) * 1.5 : -0.01) * fontSize - 1;
  const topOffset =  topOffsetPx + 'px' // -0.01 rem is a hack fix for an annoying space that happens above sticky accordions, due to our global font size of 13px leading to half-pixel sizings with tailwind top-2, etc.

  React.useEffect(() => {

    const scrollToAccordion = (e) => {
      const data = e.detail;
      if (elementId === data?.id) {
        const isOpening = !isOpen;
        setIsOpen(true);
        if (isOpening) {
          triggerResize();
        }
        const accordion = document.getElementById(elementId);
        const accordionYPos = accordion?.getBoundingClientRect().top;
        const accordionOffsetY = accordion?.offsetTop;
        // console.log('accordionOffsetY:', accordionOffsetY, 'accordionYPos:', accordionYPos, 'topOffsetPx:', topOffsetPx)
        const scrollWrapperId = isComparisonMode ? 'columns-wrapper' : 'non-comparison-results-scroll-wrapper';
        const scrollWrapper = document.getElementById(scrollWrapperId);
        if (accordion && scrollWrapper && accordionYPos !== undefined && accordionOffsetY !== undefined) {
          let deltaScrollY: number;
          if (isComparisonMode) {
            deltaScrollY = accordionYPos - topOffsetPx;
          } else {
            const accordionHeaderHeight = accordion.getElementsByClassName('accordion-header')?.[0].clientHeight || 0;
            deltaScrollY = accordionYPos - topOffsetPx - scrollWrapper.offsetTop - accordionHeaderHeight;
          }
          setTimeout(() => {
            scrollWrapper.scrollBy({
              top: deltaScrollY, 
              left: 0, 
              behavior: 'smooth' 
            });
          }, 1)
        }
      }
    }

    document.addEventListener('scrollToAccordion', scrollToAccordion)

    return () => {
      document.removeEventListener('scrollToAccordion', scrollToAccordion)
    }
  })


  return (
    <div
      className={`accordion ${wrapperClassName ? wrapperClassName : ''} ${isOpen ? 'accordion-open' : 'accordion-closed'}`}
      id={elementId}
    >
      {/* <div className="py-1 px-2 bg-red-500 text-white">Accordion rendered {(renderCount.current ++)} time(s)</div> */}

      <div
        className={`accordion-header group ${stickyHeader ? `sticky gutter-l pr-4 z-10 mb-0 border-t border-b border-gray-300 shadow-sm mt-[-1px]` : 'rounded'} ${theme === 'no-background' ? (isComparisonMode ? 'pl-3 mt-4' : 'gutter-l mt-4') : `bg-gray-100 gutter-l py-2`} ${padContentTop ? 'mb-2' : ''} cursor-pointer flex items-center text-md select-none leading-5 ${isComparisonMode && headerLayout === 'comparisonRow' ? '!p-0 items-stretch' : ''} ${headerClassName ? headerClassName : ''}`}
        onClick={() => {
          const isOpening = !isOpen;
          setIsOpen(!isOpen);
          if (isOpening) {
            triggerResize();
          }
        }}
        style={{top: topOffset, marginTop: stickyHeader ? '-1px' : ''}}
      >
        <div className={`${isComparisonMode && headerLayout === 'comparisonRow' ? 'comparison-sidebar' : 'flex-shrink-0'}`}>
          <div className="flex">
            <div className="flex items-center">
              <motion.span
                className={`inline-block mr-2 h-6 w-6 leading-[1.4em] text-center rounded-full ${theme === 'subtle' ? 'text-gray-600' : 'text-purple-800'}`}
                animate={{transform: `rotateZ(${isOpen ? '90' : '00'}deg)`}}
                style={{transformOrigin: 'center'}}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                {/* } */}
              </motion.span>
              {title &&
                <span className={`${theme === 'subtle' ? 'text-gray-500 font-normal' : 'text-gray-600 font-bold'} ${isComparisonMode && headerLayout === 'comparisonRow' ? '' : 'mr-8'} ${titleClassName ? titleClassName : ''}`}>{title}</span>
              }
            </div>
          </div>
        </div>
        {headerContent}
        {headerContentWhenOpen &&
          <motion.div
            animate={{opacity: isOpen ? 1 : 0}}
            className={`${isComparisonMode && headerLayout === 'comparisonRow' ? 'comparison-main' : 'w-full'} flex items-center z-20`}
            style={headerLayout === 'comparisonRow' ? {gridTemplateColumns: `repeat(${comparisonCases?.length || 1}, minmax(0px, 1fr))`} : {}}
            onClick={(e) => e.stopPropagation()}
          >
            {headerContentWhenOpen}
          </motion.div>
        }
        {headerContentWhenClosed && !isOpen &&
          // <motion.div
          //   animate={{opacity: isOpen ? 0 : 1}}
          //   className={`${isComparisonMode && headerLayout === 'comparisonRow' ? 'comparison-main' : 'w-full'} flex items-center z-20`}
          //   style={headerLayout === 'comparisonRow' ? {gridTemplateColumns: `repeat(${comparisonCases?.length || 1}, minmax(0px, 1fr))`} : {}}
          //   onClick={(e) => e.stopPropagation()}
          // >
          headerContentWhenClosed
          // </motion.div>
        }
      </div>
      <motion.div 
        animate={{height: isOpen ? 'auto' : 0}}
        transition={{ ease: "easeInOut"}}
        className={`${indentContent && !isComparisonMode ? 'ml-5' : ''} h-0 overflow-hidden flex flex-col ${padContentTop ? 'mt-2' : ''} accordion-content`}>
        {children}
      </motion.div>
    </div>
  );
}

Accordion.displayName = "Accordion";

export default Accordion;
