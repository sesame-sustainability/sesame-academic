import { CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon, QuestionMarkCircleIcon } from "@heroicons/react/solid";
import * as React from "react"
import toast from "react-hot-toast";
import { Button, Input } from "./styles";

export const customAlert = ({
  message,
  type = 'error',
  title,
  onConfirm,
  onCancel,
  onSubmit,
  confirmButtonText = 'Proceed',
  cancelButtonText = 'Cancel',
  dismissable = true,
}: {
  message: string | JSX.Element;
  type?: 'error' | 'confirm' | 'info' | 'prompt' | 'success' | 'custom';
  title?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
  onSubmit?: (message: string) => void;
  confirmButtonText?: string;
  cancelButtonText?: string;
  dismissable?: boolean;
}) => {

  const inputRef = React.createRef<HTMLTextAreaElement>()

  if (!title && type === 'error') {
    title === 'Error';
  }

  if (type === 'prompt') {
    confirmButtonText = 'Submit'
  }

  let iconColorClass = ''
  let icon: JSX.Element
  const iconSizeClasses = 'h-7 w-7'
  let wrapperClasses = ''
  let duration = Infinity;

  switch (type) {
    case 'error':
      iconColorClass = 'text-red-600'
      icon = (
        <svg xmlns="http://www.w3.org/2000/svg" className={`${iconSizeClasses} ${iconColorClass}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
      duration = 8000
      break
    case 'confirm':
      iconColorClass = 'text-orange-400'
      icon = <ExclamationCircleIcon className={`${iconSizeClasses} ${iconColorClass}`} />
      break
    case 'info':
      iconColorClass = 'text-blue-400'
      icon = <InformationCircleIcon className={`${iconSizeClasses} ${iconColorClass}`} />
      duration = 6000
      break
    case 'success':
      iconColorClass = 'text-emerald-500'
      icon = <CheckCircleIcon className={`${iconSizeClasses} ${iconColorClass}`} />
      duration = 2000
      break
    case 'custom':
      wrapperClasses = 'w-3/4 max-w-6xl aspect-[20/8]'
      break
  }

  toast.remove();
  
  toast.custom((t) => (

    <div className={`bg-white max-w-xl rounded-lg border-gray-200 border p-5 shadow-lg ${
      t.visible ? 'animate-enter' : 'animate-leave'
    } ${wrapperClasses}`}>
      <div className="flex flex-row items-start flex-initial">
        <div className="pr-2">
          {icon}
        </div>
        <div className="ml-2 mr-6 flex-grow">
          {title &&
            <div className="text-lg font-semibold text-gray-500 mb-2">{title}</div>
          }
          <div>{message}</div>
          {type === 'confirm' && onConfirm &&
            <div className="mt-4 flex flex-wrap">
              <Button
                onClick={() => {
                  onConfirm();
                  toast.dismiss(t.id);
                }}
                className="mb-2 !whitespace-normal mr-4"
                id="custom-alert--confirm"
              >{confirmButtonText}</Button>
              <Button 
                onClick={() => {
                  onCancel && onCancel()
                  toast.dismiss(t.id)
                }}
                color="gray"
                className="!whitespace-normal"
                id="custom-alert--cancel"
              >{cancelButtonText}</Button>
            </div>
          }
          {type === 'prompt' &&
            <div>
              <form onSubmit={(e) => handleSubmit()}>
                <textarea ref={inputRef} className="w-full mt-4 mb-2 rounded !border-gray-300" />
              </form>
              {/* <Input className="px-2" placeholder="Feedback here" /> */}
              <Button
                onClick={() => {
                  // onConfirm();
                  toast.dismiss(t.id);
                  handleSubmit();
                }}
                className="mb-2 !whitespace-normal mr-4"
                id="custom-alert--confirm"
              >{confirmButtonText}</Button>
              <Button 
                onClick={() => {
                  onCancel && onCancel()
                  toast.dismiss(t.id)
                }}
                color="gray"
                className="!whitespace-normal"
                id="custom-alert--cancel"
              >{cancelButtonText}</Button>
            </div>
          }
          {/* <span className="block text-gray-400">Anyone with a link can now view this file</span> */}
        </div>
        {dismissable &&
          <svg onClick={() => toast.dismiss(t.id)} xmlns="http://www.w3.org/2000/svg" className="cursor-pointer flex-shrink-0 hover:text-gray-600 h-6 w-6 rounded transition-colors text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        } 
      </div>
    </div>
  ), {
    duration
  });
}
