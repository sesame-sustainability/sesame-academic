import React from "react";
import * as Styles from "./styles";
import { capitalize } from "lodash"
import { InputBlock } from "./userInputs";

export const DirectionPicker = ({
  startsWith,
  setStartsWith,
}: {
  setStartsWith: React.Dispatch<AnalysisDirection>;
  startsWith: AnalysisDirection;
}): JSX.Element => {
  return (
    <span className="relative inline-flex mb-1">
      {['enduse', 'upstream'].map((value, index) => {
        return (
          <Styles.Button
            key={value}
            onClick={() => {
              // TO DO: if pathway, clear first
              setStartsWith(value);
            }}
            type="button"
            color={startsWith === value ? '' : 'gray'}
            attachedDirection={index === 0 ? 'right' : 'left'}
            size="small"
            // className={`relative inline-flex items-center px-4 py-2 border bg-white leading-5 font-medium hover:text-gray-500 focus:z-10 focus:outline-none focus:border-blue-300 focus:shadow-outline-blue active:bg-gray-100 active:text-gray-700 transition ease-in-out duration-150
            //   ${index === 0 ? 'rounded-l border-r-0' : 'rounded-r'} 
            //   ${startsWith === value ? "border-blue-400 bg-blue-500 text-blue-900" : "border-gray-400 text-gray-700"} 
            // `}
          >
            Start with {capitalize(value)}
          </Styles.Button>
        )
      })}
    </span>
  );
};
export const CategoricalSelect = ({
  name,
  value,
  options,
  setTarget,
  className,
}: {
  name: string;
  value: string;
  options: { [name: string]: string[] };
  setTarget: (val: string) => void;
  className?: string;
}): JSX.Element => {
  return (
    <Styles.Select
      className={className ?? ""}
      disabled={!options || !options[name] || options[name].length === 0 || options[name].length === 1}
      id={`user-inputs--select-${name}`}
      value={value}
      onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
        setTarget(e.target.value)
      }
    >
      <option key="none" value="" disabled>
        Select one
      </option>
      {options &&
        Object.keys(options[name] || {}).map((index, idx) => {
          return (
            <option key={idx}>{options[name][parseInt(index, 10)]}</option>
          );
        })}
    </Styles.Select>
  );
};

export const SourceSelect = ({
  sourceId,
  sources,
  onChange,
}: {
  sourceId: string;
  sources?: Source[];
  onChange?: (value: string) => void;
}): JSX.Element | null => {
  return (
    <InputBlock layout="column">
      <Styles.Label htmlFor="sources">Data Source</Styles.Label>
      <div className="relative">
        <Styles.Select
          id="sources"
          value={sourceId}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            if (onChange) {
              onChange(e.target.value);
            }
          }}
        >
          <option key="none" value="0">
            Select a source
          </option>
          {sources
            ? sources.map(({ name, id }) => (
                <option key={id} value={`${id}`}>
                  {name}
                </option>
              ))
            : null}
        </Styles.Select>
      </div>
    </InputBlock>
  );
};

export const CategorySelect = ({
  category,
  categories,
  onChange,
}: {
  category: string;
  categories?: string[];
  onChange?: (value: string) => void;
}): JSX.Element => {
  return (
    <InputBlock layout="column">
      <Styles.Label htmlFor="categories">Category</Styles.Label>
      <Styles.Select
        id="categories"
        value={category}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
          if (onChange) {
            onChange(e.target.value);
          }
        }}
      >
        <option key="none" value="0">
          Select a category
        </option>
        {categories
          ? categories.map((c, idx) => (
              <option key={idx} value={c}>
                {c}
              </option>
            ))
          : null}
      </Styles.Select>
    </InputBlock>
  );
};

export const ActivitySelect = ({
  activityId,
  activities,
  disabled,
  onChange,
}: {
  activityId: string;
  disabled: boolean;
  activities?: Activity[];
  onChange?: (value: string) => void;
}): JSX.Element => {
  return (
    <InputBlock layout="column">
      <Styles.Label htmlFor="activities">Activity</Styles.Label>
      <div className="relative">
        <Styles.Select
          disabled={disabled}
          id="activities"
          value={activityId}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            if (onChange) {
              onChange(e.target.value);
            }
          }}
        >
          <option key="none" value="0">
            Select an activity
          </option>
          {activities
            ? activities.map(({ name, id }) => (
                <option key={id} value={`${id}`}>
                  {name}
                </option>
              ))
            : null}
        </Styles.Select>
      </div>
    </InputBlock>
  );
};

export const PathwayNameInput = ({
  pathwayName,
  setPathwayName,
}: {
  pathwayName: string;
  setPathwayName: (value: string) => void;
}): JSX.Element => {
  return (
    <div className="max-w-xs">
      <Styles.Label
        htmlFor="pathway-name"
      >
        Pathway name
      </Styles.Label>
      <div className="">
        <Styles.Input
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setPathwayName(e.target.value)
          }
          type="text"
          value={pathwayName}
          id="pathway-name"
          placeholder="My Pathway"
        />
      </div>
    </div>
  );
};
