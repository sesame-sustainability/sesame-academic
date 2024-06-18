import { Menu, Transition } from '@headlessui/react'
import * as React from 'react'
import { Fragment, useEffect, useRef, useState } from 'react'
import { ChevronDownIcon } from '@heroicons/react/solid'
import { getCaseNameFromComparisonCaseAtIndex, ModuleDispatchContext, ModuleStateContext, setSavedItemNameById } from './comparableResultsModule'
import { useLiveQuery } from 'dexie-react-hooks'
import { db } from '../hooks/useDB'
import { capitalize, generateUniqueIntId, unique } from '../utils'
import { Button, Label } from './styles'
import { Link } from 'gatsby'
import { customAlert } from './customAlert'

export const SavedItemMenu = ({
  comparisonIndex,
  activeItem,
  activeItemId,
  activeItemName,
  collectionName,
  itemTitle,
  isUnsaved = false,
  layout = 'row',
}: {
  comparisonIndex: number;
  activeItem?: ComparisonCase | ComparisonCaseBatch;
  activeItemId?: number;
  activeItemName?: string;
  collectionName: SavedItemCollectionName;
  itemTitle: string;
  isUnsaved?: boolean;
  layout?: 'row' | 'column';
}) => {

  const { type, isComparisonMode, subModuleType } = React.useContext(ModuleStateContext) as ModuleStateProps;
  const dispatch = React.useContext(ModuleDispatchContext)
  // const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const buttonRef = React.useRef<HTMLButtonElement>();

  const savedItems = useLiveQuery(
    () => {
      if (type && collectionName in db) {
        return db[collectionName].filter(item => {
          let isVisible = item.type === type && !item.isDemo
          if (collectionName === 'savedCases' && subModuleType && item.subModuleType !== subModuleType) {
            isVisible = false
          }
          return isVisible
        }).sortBy('sortIndex')
      } else {
        return []
      }
    },
    [type, subModuleType] // dependencies list here
  ) as Array<ComparisonCase | ComparisonCaseBatch>

  // const currentItemName = savedItems?.find(savedItem => savedItem.id === comparisonItemId)?.name || getItemNameFromComparisonItemAtIndex(comparisonItems?.[comparisonIndex], comparisonIndex);
  // const currentItemName = getCurrentItemName();

  const getItemNameById = (id: number) => {
    return savedItems?.find(savedItem => savedItem.id === id)?.name;
  }

  const isActiveItemReadOnly = activeItem?.isDemo;

  const menuItemClasses = "py-1 px-4 flex items-center cursor-pointer hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:bg-gray-100 focus:text-gray-900";

  const closeMenu = () => {
    buttonRef?.current?.click();
  }

  const [checkedIds, setCheckedIds] = React.useState<number[]>([]);

  useEffect(() => {
    setCheckedIds([]);
  }, [JSON.stringify(savedItems?.map(savedItem => savedItem.id))])

  const delaySetCheckedIds = () => {
    setTimeout(() => {
      setCheckedIds([]);
    }, 1);
  }

  const toggleItemIdChecked = (id: number) => {
    const isItemIdAlreadyChecked = checkedIds.some(checkedId => checkedId === id);
    if (isItemIdAlreadyChecked) {
      setCheckedIds([...checkedIds].filter(checkedId => checkedId !== id));
    } else {
      setCheckedIds(unique([...checkedIds].concat(id)) || []);
    }
  }

  const deleteSavedItemIds = (ids: number[]) => {
    switch (collectionName) {
      case 'savedCases':
        dispatch({type: 'deleteSavedCaseIds', value: ids});
        break;
      case 'savedBatches':
        dispatch({type: 'deleteSavedBatchIds', value: ids})
        break;
      default:
        break;
    }
  }

  return (
    <div className={`flex ${layout === 'column' ? 'flex-col space-y-1' : 'items-center mr-3'} min-w-0 max-w-full`}>
      {/* {!isComparisonMode &&
        <span className="text-gray-300">•</span>
      } */}
      <Label className={`mr-2 text-gray-500 ${isComparisonMode ? '' : 'ml-6'}`}>{itemTitle}:</Label>
      <div className="flex items-center">
        <div className="text-left min-w-0 flex-1">{/*} fixed top-4">*/}
          <Menu as="div" className="relative w-full text-left" id={`saved-${itemTitle.toLowerCase()}-menu-${comparisonIndex}`}>
            {({ open }) => {
              if (!open) {
                if (checkedIds.length > 0) {
                  delaySetCheckedIds();
                }
              }
              return (
                <>
                  <div>
                    <Menu.Button ref={buttonRef} className="flex flex-row w-full px-4 py-1 bg-white font-medium text-gray-700 border border-gray-300 rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75">
                      <span style={{textOverflow: 'ellipsis'}} className={`overflow-hidden whitespace-nowrap saved-${itemTitle.toLowerCase()}-name`}>{activeItemName || `New ${capitalize(itemTitle)}`}</span>{/*isUnsaved && '*'*/}
                      <ChevronDownIcon
                        className="w-5 h-5 ml-2 -mr-1 text-violet-200 hover:text-violet-100"
                        aria-hidden="true"
                      />
                    </Menu.Button>
                  </div>
                  <Transition
                    as={Fragment}
                    enter="transition ease-out duration-100"
                    enterFrom="transform opacity-0 scale-100"
                    enterTo="transform opacity-100 scale-100"
                    leave="transition ease-in duration-75"
                    leaveFrom="transform opacity-100 scale-100"
                    leaveTo="transform opacity-0 scale-100"
                  >
                    <Menu.Items className={`saved-${itemTitle.toLowerCase()}-dropdown z-30 absolute left-0 w-80 mt-1 origin-top-right bg-white divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none`}>
                    
                      {collectionName === 'savedCases' &&
                        <div 
                          className={menuItemClasses}
                          onClick={() => {
                            if (checkedIds.length === 0) {
                              // when choosing New Item (id=''), set inputValues to null instead of just clearing the item, which would set data to undefined (and useUserInputs would NOT recalculate defaults, which is the desired behavior when you change an input value after loading a saved item), so we make sure to reset inputs to defaults
                              dispatch({type: 'resetComparisonCaseAtIndex', index: comparisonIndex})//, value: {id: generateUniqueIntId(), data: {inputValues: null}}})
                              closeMenu();
                            }
                          }}
                        >
                          New {itemTitle.toLowerCase()}
                        </div>
                      }
                  
                      <div>
                        {savedItems?.map((savedItem, index) => {
                          return (
                            <div
                              key={savedItem.id}
                              className={`saved-${itemTitle.toLowerCase()}-menu-item ${menuItemClasses}`}
                              onClick={() => {
                                if (checkedIds.length === 0) {
                                  if (collectionName === 'savedCases') {
                                    dispatch({type: 'setComparisonCaseIdAtIndex', index: comparisonIndex, value: savedItem.id, dispatch: dispatch })
                                  } else if (collectionName === 'savedBatches') {
                                    // const shouldLoadBatch = confirm('');
                                    customAlert({
                                      title: 'Warning',
                                      message: 'Loading a batch will clear all active cases. Proceed?', 
                                      type: 'confirm',
                                      onConfirm: () => {
                                        dispatch({type: 'loadBatchId', value: savedItem.id, dispatch: dispatch })
                                      }
                                    });
                                  }
                                  closeMenu();
                                } else {
                                  // console.log(savedItem.id);
                                  toggleItemIdChecked(savedItem.id);
                                  // toggle
                                  // setCheckedIds(unique([...checkedIds].concat(savedItem.id)));
                                }
                              }}
                            >
                              <input
                                type="checkbox"
                                className="rounded border-gray-300 mr-2 h-5 w-5"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleItemIdChecked(savedItem.id);
                                }}
                                onChange={(e) => {}} // to squelch react error msg about not having onchange
                                checked={checkedIds.some(id => id === savedItem.id)}
                              />
                              <a className={`${savedItem.id === activeItemId ? 'font-bold' : ''}`} key={index}>{savedItem.name}</a>
                              <svg
                                className="flex-shrink-0 cursor-pointer ml-auto h-7 w-7 p-1 text-gray-400 hover:text-red-500 group-focus:text-gray-500"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  const shouldDelete = confirm('Delete "' + getItemNameById(savedItem.id) + '"?')
                                  if (shouldDelete) {
                                    deleteSavedItemIds([savedItem.id]);
                                    closeMenu();
                                  }
                                }}
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            </div>
                          )
                        })}
                      </div>
                      {savedItems?.length > 0 &&
                        <div className={menuItemClasses}>
                          {checkedIds.length === 0 ?
                            <Button
                              size="small"
                              className="my-1"
                              onClick={() => {
                                setCheckedIds(savedItems.map(savedItem => savedItem.id));
                              }}
                            >Select all</Button>
                          :
                            <Button
                              color="red"
                              size="small"
                              className="my-1"
                              onClick={() => {
                                const shouldDelete = confirm(`Really delete ${checkedIds.length} saved item(s)?`)
                                if (shouldDelete) {
                                  deleteSavedItemIds(checkedIds);
                                  closeMenu();
                                }
                              }}
                            >Delete selected</Button>
                          }
                        </div>
                      }
                      <Link to={`/app/saved?moduleType=${type}`} className={menuItemClasses}>
                        More actions...
                      </Link>
                    
                      {/* <div
                        className={menuItemClasses}
                        onClick={() => {
                          // when choosing New Item (id=''), set inputValues to null instead of just clearing the item, which would set data to undefined (and useUserInputs would NOT recalculate defaults, which is the desired behavior when you change an input value after loading a saved item), so we make sure to reset inputs to defaults
                          dispatch({type: 'setComparisonItemAtIndex', index: comparisonIndex, value: {id: '', data: {inputValues: null}}})
                          closeMenu();
                        }}
                      >
                        Reset to Defaults
                      </div> */}

                    </Menu.Items>
                  </Transition>
                </>
              )
            }}
          </Menu>
        </div>
        {!!activeItemId && !isUnsaved && !isActiveItemReadOnly &&
          <EditItemNameButton
            itemId={activeItemId}
            collectionName={collectionName}
            comparisonIndex={comparisonIndex}
            setItemName={(name: string) => {
              if (collectionName === 'savedCases') {
                dispatch({type: 'setComparisonCasePropsAtIndex', index: comparisonIndex, value: { name }});
              } else if (collectionName === 'savedBatches') {
                dispatch({type: 'setBatchProps', value: { name }})
              }
              setSavedItemNameById(activeItemId, name, collectionName);
            }}
          />
        }
      </div>
    </div>
  )
}

export const EditItemNameButton = ({
  itemId,
  comparisonIndex,
  collectionName,
}: {
  itemId: number;
  comparisonIndex?: number;
  collectionName: SavedItemCollectionName;
}) => {

  const dispatch = React.useContext(ModuleDispatchContext);

  return (
    <Button
      size="xs"
      color="gray"
      className={`ml-2 edit-item-name edit-${collectionName}-name`}
      title="Edit item name"
      onClick={(e) => {
        e.stopPropagation();
        const name = prompt('Choose a new name:');
        if (name) {
          if (typeof dispatch === 'function') { // otherwise we're not in a ComparableResultsModule, and don't have to worry about updating module state - i.e. we're in Saved Cases page
            if (collectionName === 'savedCases') {
              dispatch({type: 'setComparisonCasePropsAtIndex', index: comparisonIndex, value: { name }});
            } else if (collectionName === 'savedBatches') {
              dispatch({type: 'setBatchProps', value: { name }})
            }
          }
          console.log(itemId, name, collectionName)
          setSavedItemNameById(itemId, name, collectionName);
          // setItemName(newName);
        }
      }}
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
      </svg>
    </Button>
  )
}