// import { Transition } from "@headlessui/react";
import React from "react";
// import ReactDOM from "react-dom"
import Portal from "./portal"
// import { Transition } from "@headlessui/react";

const colorClassMapping = {
  'dark-gray': 'bg-gray-700 text-gray-200',
  'green': 'bg-gradient-to-r from-lime-600 to-emerald-600 text-white',
  'purple': 'bg-gradient-to-r from-indigo-700 to-purple-700 text-white',
}

const Modal: React.FunctionComponent<{
  showModal: boolean;
  title?: string| JSX.Element;
  message?: JSX.Element;
  showIcon?: boolean;
  wrapperClasses?: string;
  headerColor?: "dark-gray" | "green" | "purple";
  // dismissable?: boolean;
  onClose?: () => void;
}> = ({ showModal, title, message, showIcon, wrapperClasses, headerColor = "dark-gray", onClose, children }) => {

  const headerColorClasses = colorClassMapping[headerColor]

  return (
    showModal ?
    <Portal>
      {/* <Transition
        show={showModal}
        enter="ease-out duration-300"
        enterFrom="opacity-0"
        enterTo="opacity-100"
        leave="ease-in duration-200"
        leaveFrom="opacity-100"
        leaveTo="opacity-0"
      > */}
        <div className="fixed z-50 inset-0 overflow-y-auto animate-fade-in">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center p-0">
            <div className="fixed inset-0 transition-opacity">
              <div className="absolute inset-0 bg-gray-900 opacity-70"></div>
            </div>
            <div
              className={`bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all my-8 align-middle max-w-sm w-full p-6 ${wrapperClasses}`}
              role="dialog"
              aria-modal="true"
              aria-labelledby="modal-headline"
            >
              {showIcon &&
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                  <svg
                    className="h-6 w-6 text-green-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              }
              {title &&
                <div className={`text-3xl font-extralight p-4 text-center relative ${headerColorClasses}`}>
                  {title}
                  {/* {dismissable && */}
                    <div className="absolute top-0 right-0 p-4">
                      <svg onClick={() => onClose && onClose()} xmlns="http://www.w3.org/2000/svg" className="cursor-pointer flex-shrink-0 opacity-80 hover:opacity-100 h-8 w-8 rounded transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                  {/* } */}
                </div>
                // <div>
                //   <div className="mt-3 text-center mt-5">
                //     {title ? (
                //       <h3
                //         className="text-lg leading-6 font-medium text-gray-900"
                //         id="modal-headline"
                //       >
                //         {title}
                //       </h3>
                //     ) : null}

                //     {message ? (
                //       <div className="mt-2">
                //         <p className="text-sm leading-5 text-gray-500">{message}</p>
                //       </div>
                //     ) : null}
                //   </div>
                // </div>
              }
              {children}
            </div>
          </div>
        </div>
      {/* </Transition> */}
    </Portal>
    :
    <></>
  )
};

export default Modal;
