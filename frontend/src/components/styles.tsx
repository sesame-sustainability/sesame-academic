import React from "react";
import tw from "twin.macro";
import styled, { StyledComponent } from "@emotion/styled";

// layout
export const Col2 = styled.div`
  ${tw`md:col-span-2 sm:col-span-3`}
`;

export const ChartTitle = styled.div`
  ${tw`text-center text-lg font-semibold mt-4 mb-8 text-gray-700`}
`;

export const ChartSubtitle = styled.div`
  ${tw`text-center text-lg font-normal text-gray-600 my-4`}
`;

// forms

export const Label = styled.label<{
  displayOptions?: DisplayOptions;
}>`
  ${tw`leading-4 font-medium text-gray-700 flex items-center`}
  ${({ displayOptions }) =>
    displayOptions?.label_size === 'large' ? tw`text-lg font-bold text-gray-600` : ``
  }
  ${({ displayOptions }) => {
    let mlClass = tw``;
    switch (displayOptions?.indent_level) {
      case 1:
        mlClass = tw`ml-6`
        break
      case 2:
        mlClass = tw`ml-12`
        break
      case 3:
        mlClass = tw`ml-[4.5rem]`
        break
    }
    return mlClass;
  }}
`;

export const InputBlock = styled.div<{}>`
  ${tw`my-1`}
`
const disabledInputClasses = `bg-gray-100 cursor-not-allowed opacity-80`

export const Input = styled.input<{
  isValid?: boolean;
  disabled?: boolean;
}>`
  ${tw`block rounded w-full py-1 text-right`}
  ${({ isValid }) =>
    isValid || isValid === undefined ? tw`border border-gray-300` : tw`border-2 border-red-600`}
  ${({ disabled }) =>
    disabled ? tw`${disabledInputClasses}` : tw`` }
`;

export const Select = styled.select<{ disabled?: boolean }>`
  ${tw`rounded block w-full pl-3 pr-8 py-1 border border-gray-300 overflow-ellipsis leading-6 focus:outline-none focus:border-blue-300 appearance-none`}
  ${({ disabled }) =>
    disabled
      ? tw`${disabledInputClasses}`
      : tw``}
`;

export const InputMessage: React.FC<{
  message: string;
  className: string;
  inputName: string;
  type: 'error' | 'warning';
}> = props => {
  let colorClass;
  switch (props.type) {
    case 'error':
      colorClass = 'text-red-600';
    case 'warning':
      colorClass = 'text-yellow-600';
  }
  return (
    <p
      className={`mb-2 col-span-3 text-right ${colorClass} ${
        props.message === "" ? "invisible" : ""
      } ${props.className}`}
      id={`${props.inputName}-${props.type}`}
    >
      {props.message}
    </p>
  )
}

// export const Button: React.FC<{disabled?: boolean, isLoading?: boolean, className?: string}> = ({disabled, isLoading, className, children}) => {
//   return (
//     <button className={`${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'} inline-flex items-center px-4 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${className ? className : ''}`}>
//       {children}
//     </button>
//   )
// }


export const Loader = ({
  color = 'dark',
  size = 'large',
}: {
  color?: 'dark' | 'light',
  size?: 'small' | 'large',
}) => {

  let colorClass;
  if (color === 'dark') {
    colorClass = 'text-gray-800'
  } else if (color === 'light') {
    colorClass = 'text-gray-300'
  }

  let sizeClass;
  if (size === 'large') {
    sizeClass = 'h-10 w-10'
  } else if (size === 'small') {
    sizeClass = 'h-6 w-6'
  }

  return (
    <div className={`flex items-center justify-center`}>
      <svg className={`inline-block animate-spin mx-auto ${sizeClass} ${colorClass}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  )
}

export const Button = styled.button<{
  disabled?: boolean;
  color?: 'blue' | 'gray' | 'dark-gray' | 'medium-gray' | 'green' | 'red';
  attachedDirection?: 'right' | 'left';
  size?: 'large' | 'small' | 'xs';
  width?: 'snug' | 'tight' | 'square';
}>`
  ${({ disabled }) =>
    disabled ? tw`opacity-50 cursor-not-allowed` : null}
  ${({ color }) => {
    switch (color) {
      case 'blue':
        return tw`text-white bg-blue-600 hover:bg-blue-700 hover:text-white`
      case 'gray':
        return tw`text-gray-500 bg-gray-200 hover:bg-gray-300`;
      case 'dark-gray':
        return tw`text-gray-200 bg-gray-700 hover:bg-gray-600`
      case 'medium-gray':
        return tw`text-gray-200 bg-gray-500 hover:bg-gray-400`
      case 'green':
        return tw`text-white bg-gradient-to-br from-lime-600 to-green-600 hover:to-green-700`;
      case 'red':
        return tw`text-white bg-red-500 hover:bg-red-600`
      default:
        return tw`text-gray-200 bg-gray-700 hover:bg-gray-600`
      }
    }
  }

  ${({ attachedDirection }) => {
    if (attachedDirection === 'right') {
      return tw`rounded-l`
    } else if (attachedDirection === 'left') {
      return tw`rounded-r`
    } else {
      return tw`rounded`
    }
  }}
  ${({ size }) => {
    switch (size) {
      case 'small':
        return tw`text-sm leading-5 px-3 py-2 h-9`
      case 'xs':
        return tw`text-sm leading-5 px-2 py-1 h-8`
      case 'large':
        return tw`text-base px-4 py-4 h-12`
      default:
        return tw`text-base px-3 py-3 h-9`
    }
  }}
  ${({ width, size }) => {
    return null;
    // switch (width) {
    //   case 'snug':
    //     return tw`px-4`
    //   case 'tight':
    //     return tw`px-2`
    //   case 'square':
    //     if (size === 'small') {
    //       return tw`w-10 px-3`
    //     } else if (size === 'xs') {
    //       return tw`w-8`
    //     } else {
    //       return tw`w-10`
    //     }
    //   default:
    //     return tw`px-6`
    // }
  }}
  ${tw`whitespace-nowrap inline-flex items-center select-none font-medium focus:outline-none focus:ring-2 focus:ring-blue-500`};
`;

export const RunButton: React.FC<{loading?: boolean, disabled?: boolean, label?: string, className?: string, onClick?: () => Promise<void>}> = ({loading, disabled, label, className, onClick, ...props}) => {
  return (
    <Button {...props} onClick={onClick} disabled={disabled || loading} size="small" className={`w-16 ml-3 justify-center run-button ${className ? className : ''}`}>
      {loading ?
        <>
          <svg className="inline animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </>
      : (label || "Run")}
    </Button>
  )
}

export const SquareButton: React.FC = ({...props}) => {
  return (
    <Button {...props} className="w-10 h-10">{props.children}</Button>
  )
}

// graphs
export const GraphSelect: React.FunctionComponent = ({ children }) => {
  return (
    <div
      style={{
        marginTop: "1rem",
        marginLeft: "1rem",
        position: "absolute",
        width: "max-content",
        zIndex: 1,
      }}
    >
      <div className="relative">{children}</div>
    </div>
  );
};

export const formatNegativePercent = (formattedNumStr: string): JSX.Element => {
  if (formattedNumStr.charAt(0) === "-") {
    return (
      <div className="text-3xl text-red-500">
        {`▼${formattedNumStr.replace("-", "")}`}%
      </div>
    );
  } else {
    return (
      <div className="text-3xl text-green-500">
        {`▲${formattedNumStr.replace("-", "")}`}%
      </div>
    );
  }
};

export const ChartWrapper = styled.div`
  min-height: 420px;
  ${tw`shadow-md bg-white relative pb-4 px-2 pt-1`}
`;

export const ClickToZoom = (): JSX.Element => (
  <>
    <div
      className="block md:hidden absolute bottom-0 left-0 mb-4 ml-4 text-gray-700"
      style={{ fontSize: "0.85rem" }}
    >
      *Pinch to zoom/pan
    </div>
    <div
      className="hidden md:block absolute bottom-0 left-0 mb-4 ml-4 text-gray-700"
      style={{ fontSize: "0.85rem" }}
    >
      *Click and drag to zoom
    </div>
  </>
);

// badges
export const CategoryBadge = styled.span<{ category: string }>`
  ${tw`px-2 inline-flex text-sm leading-5 font-semibold rounded-full`}
  ${({ category }) => {
    switch (category) {
      case "Electricity":
        return tw`bg-yellow-100 text-yellow-700`;
      case "Chemical":
        return tw`bg-green-100 text-green-700`;
      case "Fuel":
        return tw`bg-purple-100 text-purple-700`;
      case "No category":
        return tw`bg-gray-100 text-gray-700`;
    }
  }}
`;

export const H2: React.FunctionComponent = ({ children }) => (
  <h2 className="text-xl font-semibold text-gray-600 leading-6 sm:truncate mb-5">
    {children}
  </h2>
);

export const A = styled.a`
  ${tw`font-medium text-gray-500 underline`}
`

export const HR = () => (
  <div className="border-b border-gray-100 my-6"></div>
)
