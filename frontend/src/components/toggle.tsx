import * as React from "react"
import * as Styles from './styles'

export const Toggle = ({
  label,
  value,
  setValue,
  className,
  id,
  isDisabled,
  isErroneous,
}: {
  label: string;
  value: boolean;
  setValue: (value: boolean) => void;
  className?: string;
  id?: string;
  isDisabled?: boolean;
  isErroneous?: boolean;
}) => {
  return (
    <div className={`w-full my-1 ${className ? className : ''}`}>
      <label className={`flex items-center`}>
        <div className={`relative ${isDisabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
          <input type="checkbox" disabled={isDisabled} onChange={ (e) => { setValue(!value) } } className="sr-only" />
          <div
            className={`block bg-gray-300 transition-colors ${value ? 'bg-green-500' : ''} ${isDisabled ? 'opacity-50' : ''} rounded-full ${isErroneous ? '!border-red-600 !border-2' : ''}`}
            style={{height: '22px', width: '42px'}}
            
          >
          </div>
          <div
            className={`absolute bg-white h-[18px] w-[18px] top-[2px] rounded-full transition-all left-[2px] ${value ? 'left-[22px]' : ''}`}
            // style={isYAxisLocked ? {transform: 'translateX(100%)'} : {}}
            // style={{height: '20px', width: '20px', top: '2px', left: isYAxisLocked ? '20px' : '2px'}}
            id={`toggle--${id}`} 
          >
          </div>
        </div>
        <Styles.Label className="ml-3">
          {label}
        </Styles.Label>
      </label>
        
    </div>
  )
}