import React from 'react';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css'; // optional

export const Tooltip = ({
  data,
  children
}: {
  data?: TooltipData,
  children?: React.ReactElement,
}) => {

  if (!data) {
    return null;
  }

  const { content, source, source_link } = data;

  if (!content && !source) {
    return null;
  }

  return (
    <Tippy
      interactive={source_link ? true : false}
      appendTo={document.body}
      offset={[0,10]}
      content={
        <>
          {content &&
            <div>{content}</div>
          }
          {source &&
            <div className="text-sm text-gray-400">
              Default source: {
                source_link ? (
                  <a href={source_link} target="_blank">{source}</a>
                ) : (
                  source
                )
              }
            </div>
          }
        </>
      }
    >
      <span className={children ? '' : 'ml-2'}>
        {children ?
          children
          :
          <svg xmlns="http://www.w3.org/2000/svg" className="inline-block h-6 w-6 text-gray-300 hover:text-gray-800 transition-colors" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>  
        }
      </span>
    </Tippy>
  )  
};