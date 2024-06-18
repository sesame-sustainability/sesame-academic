import { DocumentDuplicateIcon, ExternalLinkIcon, PlusCircleIcon, TrashIcon } from "@heroicons/react/solid";
import { DotsVerticalIcon, FolderAddIcon } from "@heroicons/react/outline";
import { useLiveQuery } from "dexie-react-hooks";
import { Link, navigate } from "gatsby";
import * as React from "react";
import { SortableContainer, SortableElement, SortableHandle } from 'react-sortable-hoc';
import { arrayMoveImmutable } from 'array-move';
import { db, useSavedCases } from "../../hooks/useDB";
import { comparableResultsModules } from "../../pages/app";
import { maxComparisonResultCols } from "../../utils/constants";
import Layout from "../layout";
import { Button } from "../styles";
import { EditItemNameButton } from "../savedItemMenu";
import { customAlert } from "../customAlert";
import { deleteSavedCaseIds, saveBatch } from "../comparableResultsModule";
import Accordion from "../accordion";
import { kebabCase, unique } from "../../utils";
import SEO from "../seo";

const BulkActionButton = ({
  label,
  icon,
  onClick,
  isDisabled,
  title,
}: {
  label: string;
  icon?: JSX.Element;
  onClick: () => void;
  isDisabled?: boolean;
  title?: string;
}) => (
  <Button
    size="xs"
    disabled={isDisabled}
    onClick={() => onClick()}
    title={title}
    className={`space-x-2 mr-3 mb-2 ${kebabCase(label)}`}
  >
    {icon &&
      <span>{icon}</span>
    }
    <span>{label}</span>
  </Button>
)

const SavedItemBlock = ({
  title,
  collectionName,
  isDemo,
  allowDragDrop = true,
}: {
  title: string;
  collectionName: SavedItemCollectionName;
  isDemo?: boolean;
  allowDragDrop?: boolean;
}) => {

  const {
    cachedSavedCases,
    setCachedSavedCases,
    cachedSavedBatches,
    setCachedSavedBatches,
    // demoCases,
    // demoBatches,
    selectedModule,
    savedBatchDropzoneRefs,
    setSavedBatchDropzoneRefs,
    toggleBatchDropzoneRefHovered,
  } = React.useContext(SavedCaseBrowserContext)

  // let setCachedSavedItems: React.Dispatch<React.SetStateAction<ComparisonCaseBatch[] | ComparisonCase[]>>;
  // if (collectionName === 'savedCases') {
  //   setCachedSavedItems = setCachedSavedCases;
  // } else if (collectionName === 'savedBatches') {
  //   setCachedSavedItems = setCachedSavedBatches;
  // }
  const setCachedSavedItems = collectionName === 'savedCases' ? setCachedSavedCases : setCachedSavedBatches;
  let items: any[] = [];

  switch (collectionName) {
    case 'savedCases':
      items = cachedSavedCases.filter(o => o.isDemo === isDemo);
      break;
    case 'savedBatches':
      items = cachedSavedBatches.filter(o => o.isDemo === isDemo);
      break;
    default:
      break;
  }
  // console.log(collectionName, isDemo, items, cachedSavedCases)
  // const items = collectionName === 'savedCases' ? cachedSavedCases : (collectionName === 'savedBatches' ? cachedSavedBatches : demoCases);

  const [selectedItemIds, setSelectedItemIds] = React.useState<number[]>([])

  // const dispatch = React.useContext(ModuleDispatchContext)

  const toggleSelectItemId = (id: number) => {
    if (selectedItemIds.includes(id)) {
      setSelectedItemIds(selectedItemIds.filter(itemId => itemId !== id))
    } else {
      setSelectedItemIds(selectedItemIds.concat([id]))
    }
  }

  const onSortEnd = (e: {oldIndex: number, newIndex: number}) => {
    var newItems = arrayMoveImmutable(items, e.oldIndex, e.newIndex).map((item, index) => {
      return {
        ...item,
        sortIndex: index
      }
    })
    // if we're dragging a case onto a saved batch, then handle that - otherwise set new sort order
    if (collectionName === 'savedCases' && savedBatchDropzoneRefs.some(dropzoneRef => dropzoneRef.isHovered)) {      
      savedBatchDropzoneRefs.filter(d => d.isHovered).forEach(({savedBatchId}) => {
        const savedCaseJustDropped = items[e.oldIndex];
        console.log(savedCaseJustDropped, e.oldIndex, cachedSavedCases)
        const savedBatchJustDroppedOnto = cachedSavedBatches.find(b => b.id === savedBatchId);
        if (savedCaseJustDropped && savedBatchJustDroppedOnto) {
          const newCaseIds = savedBatchJustDroppedOnto.caseIds.concat([savedCaseJustDropped.id]);
          const maxCases = selectedModule?.maxComparisonCases || maxComparisonResultCols;
          if (newCaseIds.length > maxCases) {
            customAlert({
              type: 'error',
              message: `Only ${maxCases} cases are allowed per batch in this module`
            })
          } else {
            db.savedBatches.update(savedBatchId, {caseIds: newCaseIds})
          }
        }
      })
    } else if (e.oldIndex !== e.newIndex) { // otherwise we're setting new sort order within the same list
      // TODO fix this to be based on collectionName
      if (e.oldIndex !== e.newIndex) {

        setCachedSavedItems(newItems);
        newItems.forEach(({id, sortIndex}) => {
          db[collectionName].update(id, { sortIndex })
        })
      }
    }
    // set all saved batches as NOT hovered anymore, when we drop the saved case being dragged
    setSavedBatchDropzoneRefs(prevRefs => {
      return prevRefs.map(refObj => ({
        ...refObj,
        isHovered: false,
      }))
    })
    
  };

  return (
    <div className="py-2 gutter-x" id={`${collectionName}-block${isDemo ? '-demo' : ''}`}>
      <div className="font-bold pt-2 pb-3">{title}</div>
      <div className="flex items-center flex-wrap">
        <BulkActionButton
          label='Select all'
          isDisabled={!items?.length || selectedItemIds.length === items.length}
          onClick={() => {
            setSelectedItemIds(items.map(s => s.id));
          }}
        />
        <BulkActionButton
          label='Unselect all'
          isDisabled={!selectedItemIds.length}
          onClick={() => {
            setSelectedItemIds([]);
          }}
        />
        {collectionName === 'savedCases' &&
          <BulkActionButton
            label='Open selected'
            icon={<ExternalLinkIcon className="h-5 w-5" />}
            isDisabled={!selectedItemIds.length || selectedItemIds.length > maxComparisonResultCols}
            title={selectedItemIds.length > maxComparisonResultCols ? `Limited to ${maxComparisonResultCols} cases at once` : ''}
            onClick={() => {
              if (selectedModule) {
                navigate(`${selectedModule.path}?loadCaseIds=${selectedItemIds.join(',')}`)
              }
            }}
          />
        }
        {collectionName === 'savedCases' && !isDemo &&
          <BulkActionButton
            label='Batch selected'
            icon={<FolderAddIcon className="h-5 w-5" />}
            isDisabled={selectedItemIds.length < 1 || selectedItemIds.length > maxComparisonResultCols}
            title={selectedItemIds.length > maxComparisonResultCols ? `Limited to ${maxComparisonResultCols} cases per batch` : ''}
            onClick={() => {
              if (selectedModule) {
                saveBatch({
                  comparisonCases: items.filter(item => selectedItemIds.includes(item.id)).map(item => {return {...item, savedCaseId: item.id}}) || [], // if comparisonCases were coming from comparable results module state, its database item id would be stored as savedCaseId, and that's what saveBatch expects
                  moduleType: selectedModule.type,
                  // dispatch,
                });
              //   navigate(`${selectedModule.path}?loadCaseIds=${selectedItemIds.join(',')}`)
              }
            }}
          />
        }
        {!isDemo &&
          <BulkActionButton
            label='Delete selected'
            icon={<TrashIcon className="h-5 w-5" />}
            isDisabled={!selectedItemIds.length}
            onClick={() => {
              customAlert({
                message: `Delete ${selectedItemIds.length} selected item${selectedItemIds.length > 1 ? 's' : ''}?`,
                type: 'confirm',
                onConfirm: () => {
                  if (collectionName === 'savedCases') {
                    deleteSavedCaseIds(selectedItemIds);
                  } else {
                    db[collectionName].bulkDelete(selectedItemIds);
                  }
                  setSelectedItemIds([]);
                }
              });
            }}
          />
        }
        
      </div>
      <div className="max-w-xl">
        {collectionName === 'demoBatches'
          ? // demoBatches list is not sortable or drag-droppable. all others are (with limitations, e.g. can't reorder demo cases, but can drag/drop to your own batches)
          <SavedItemList
            items={items}
            collectionName={collectionName}
            isDemo={isDemo}
            allowSelecting={false}
          />
          :
          <SortableList
            items={items}
            collectionName={collectionName}
            isDemo={isDemo}
            onSortEnd={onSortEnd}
            allowDragDrop={allowDragDrop}
            onSortMove={(e) => {
              if (['savedCases', 'demoCases'].includes(collectionName)) {
                const x = e.pageX;
                const y = e.pageY;
                savedBatchDropzoneRefs.forEach(dropzoneRef => {
                  if (dropzoneRef.ref.current) {
                    const { top, bottom, left, right } = dropzoneRef.ref.current?.getBoundingClientRect();
                    if (x > left && x < right && y > top && y < bottom) {
                      if (!dropzoneRef.isHovered) {
                        toggleBatchDropzoneRefHovered(dropzoneRef.savedBatchId);
                      }
                    } else {
                      if (dropzoneRef.isHovered) {
                        toggleBatchDropzoneRefHovered(dropzoneRef.savedBatchId);
                      }
                    }
                  }
                })
              }
            }}
            selectedModule={selectedModule}
            selectedItemIds={selectedItemIds}
            toggleSelectItemId={toggleSelectItemId}
            useDragHandle
          />
        }
        {!selectedModule &&
          <div className="text-gray-500 py-2">Select a module above to see {title} for that module</div>
        }
        <div className="py-2">
          {selectedModule &&
            <>
              {items.length === 0 && 
                <div className="mb-3 text-gray-500">No {title.toLowerCase()} in {selectedModule?.buttonText || selectedModule?.title} {!isDemo ? 'yet' : ''}</div>
              }
              {collectionName === 'savedCases' && !isDemo &&
                <Link to={`${selectedModule?.path}`}>
                  <Button className="mt-1 mb-2">
                    {/* <ExternalLinkIcon className="h-5 w-5 mr-2 -ml-1" /> */}
                    Build case
                  </Button>
                </Link>
              }
            </>
          }
        </div>
      </div>
    </div>
  )
}

type ButtonProps = {
  label?: string;
  onClick: (item: any, index: number) => void;
  icon?: JSX.Element;
  tooltip?: string;
  isHidden?: boolean;
}

const SavedItemList = ({
  items,
  collectionName,
  selectedModule,
  selectedItemIds,
  toggleSelectItemId,
  customButtons,
  allowSelecting = true,
  allowSorting = true,
  allowDragDrop = true,
  isDemo,
}: {
  items: ComparisonCase[] | ComparisonCaseBatch[];
  collectionName: SavedItemCollectionName;
  selectedModule?: ComparableResultsModuleProps;
  selectedItemIds?: number[];
  toggleSelectItemId?: (id: number) => void;
  customButtons?: ButtonProps[];
  allowSelecting?: boolean;
  allowSorting?: boolean;
  allowDragDrop?: boolean;
  isDemo?: boolean;
}) => {

  return (
    <div className="divide-y" id={`${collectionName}-list`}>
      {items.map((item, index) => {

        const props = {
          savedItem: item,
          collectionName,
          selectedModule,
          selectedItemIds,
          toggleSelectItemId,
          customButtons,
          allowSelecting,
          allowSorting,
          index,
          itemIndex: index, // adding this to pass index down so we know which saved case index we have when it's a sub-list of a saved batch (for removing case from batch by index, not id)
          key: `${item.id}-${index}`,
          isDemo,
        }

        return (isDemo ?
          <SavedItem {...props} />
          :
          <SortableItem {...props} />
        )

        // return (allowDragDrop ?
        //   <>smoke
        //     <SortableItem {...props} />


        //   </>
        //   :
        //   <SavedItem {...props} />

        // )
      })}
    </div>
  )
}
  
const SavedItem = ({
  savedItem,
  collectionName,
  selectedItemIds,
  toggleSelectItemId,
  selectedModule,
  customButtons,
  allowSelecting,
  isDemo,
  itemIndex,
}: {
  savedItem: ComparisonCase | ComparisonCaseBatch;
  collectionName: SavedItemCollectionName;
  selectedItemIds: number[];
  toggleSelectItemId: (itemId: number) => void;
  selectedModule: ComparableResultsModuleProps | undefined;
  customButtons?: ButtonProps[];
  allowSelecting?: boolean;
  isDemo?: boolean;
  itemIndex: number;
}) => {

  const { cachedSavedBatches, setCachedSavedBatches, savedBatchDropzoneRefs } = React.useContext(SavedCaseBrowserContext)

  let ref;
  let isHovered: boolean | undefined;

  if (collectionName === 'savedBatches') {
    const matchingCachedBatch = cachedSavedBatches.find(batch => batch.id === savedItem.id);
    if (matchingCachedBatch) {
      savedItem = matchingCachedBatch;
    }
    // use refs on saved batches to track dropzones for dragging cases into batches
    const matchingDropzoneRef = savedBatchDropzoneRefs.find(dropzoneRef => dropzoneRef.savedBatchId === savedItem.id);
    if (matchingDropzoneRef) {
      ref = matchingDropzoneRef.ref;
      isHovered = matchingDropzoneRef.isHovered;
    } else {
      ref = React.createRef<HTMLDivElement>(); 
    }
  }

  let childIds: number[] = [];
  if (collectionName === 'savedBatches') {
    childIds = (savedItem as ComparisonCaseBatch)?.caseIds || [];
  }

  const childItems = (
    collectionName === 'savedBatches' && childIds.length > 0
    ?
    useLiveQuery(
      async () => {
        if (selectedModule) {
          return await db.savedCases.bulkGet(childIds)
        } else {
          return []
        }
      },
      [selectedModule, JSON.stringify(childIds)],
      [],
    ) as ComparisonCase[]
    :
    []
  ).filter(childItem => !!childItem)

  const itemActionButtons: ButtonProps[] = [
    {
      tooltip: 'Open',
      icon: <ExternalLinkIcon className="h-5 w-5" />,
      onClick: () => {
        if (selectedModule) {
          let queryString = '';
          let key = '';
          if (collectionName === 'savedCases') {
            key = `loadCaseIds`;
          } else if (collectionName === 'savedBatches') {
            key = `loadBatchId`;
          } else if (collectionName === 'demoCases') {
            key = `loadDemoCaseIds`;
          } else if (collectionName === 'demoBatches') {
            key = `loadDemoBatchId`;
          }
          navigate(`${selectedModule.path}?${key}=${savedItem.id}`)
        }
      },
    },
    {
      tooltip: 'Duplicate inputs',
      icon: <DocumentDuplicateIcon className="h-5 w-5" />,
      onClick: () => {
        if (selectedModule) {
          const caseIdsToDuplicate = collectionName === 'savedCases' ? savedItem.id : savedItem.caseIds?.join(',');
          navigate(`${selectedModule.path}?duplicateCaseIds=${caseIdsToDuplicate}`)
        }
      },
    },
    {
      tooltip: 'Delete',
      icon: <TrashIcon className="h-5 w-5" />,
      isHidden: isDemo,
      onClick: async () => {
        if (selectedModule) {
          customAlert({
            message: `Delete "${savedItem.name}"?`,
            type: 'confirm',
            onConfirm: async () => {
              if (collectionName === 'savedCases') {
                deleteSavedCaseIds([savedItem.id])
              } else if (collectionName === 'savedBatches') {
                const caseIds: number[] = (savedItem as ComparisonCaseBatch).caseIds || [];
                const promises: Promise<{id: number, name: string, isDangling: boolean} | undefined>[] = [];
                caseIds?.forEach(caseId => {
                  promises.push(
                    db.savedBatches.filter((batch) => {
                      // see if there are any other saved batches that use this case ID (if not, delete it)
                      return batch.caseIds?.includes(caseId) && batch.id !== savedItem.id
                    }).count().then(async (numBatchesIncludedIn) => {
                      const isDangling = numBatchesIncludedIn === 0;
                      let returnProps;
                      if (isDangling) {
                        const matchingCase = await db.savedCases.get(caseId);
                        if (matchingCase) {
                          returnProps = {
                            id: caseId,
                            isDangling,
                            name: matchingCase.name,
                          };
                        }
                      }
                      return returnProps;
                      // if (total === 0) {
                      //   db.savedCases.delete(savedCase.id);
                      // }
                    })
                  )
                })
                try {
                  const savedCasesInBatchWithDanglingState = await Promise.all(promises).catch(e => {
                    console.log(e);
                  })
                  const danglingCases = savedCasesInBatchWithDanglingState?.filter(savedCase => savedCase?.isDangling);
                  if (danglingCases && danglingCases.length > 0) {
                    customAlert({
                      type: 'confirm',
                      message: 
                        <>
                          <div>The following cases in this batch are not included in any other batches:</div>
                          <ul className="list-disc py-4 pl-6">
                            {danglingCases?.map(danglingCase => (
                              <li>{danglingCase?.name}</li>
                            ))}
                          </ul>
                          <div>Do you want to delete them too?</div>
                        </>,
                      confirmButtonText: 'Delete',
                      cancelButtonText: 'Keep',
                      onConfirm: () => {
                        const caseIdsToDelete = danglingCases?.map(d => d ? d.id : -1).filter(id => id >= 0) || [];
                        if (caseIdsToDelete.length > 0) {
                          deleteSavedCaseIds(caseIdsToDelete)
                          // db.savedCases.bulkDelete(caseIdsToDelete)
                        }
                      }
                    })
                  }
                } catch (error) {
                  console.log(error);
                }
                db.savedBatches.delete(savedItem.id);
              }
            }
          })
        }
      },
    },
  ]

  const isAccordion = collectionName === 'savedBatches';

  const buttons = customButtons || itemActionButtons;

  const savedItemContent = (
    <>
      <div className={!isAccordion ? 'mt-[0.3rem]' : ''}>{savedItem.name}</div>
      <div className="ml-auto space-x-2 flex items-center">
        {!customButtons && !isDemo &&
          <EditItemNameButton
            collectionName={collectionName}
            itemId={savedItem.id}
          />
        }
        {buttons.map(button => (
          !button.isHidden ?
            <Button
              title={button.tooltip}
              key={button.label}
              className={kebabCase(button.tooltip)}
              onClick={(e) => {
                e.stopPropagation();
                if (button.onClick) {
                  button.onClick(savedItem, itemIndex)
                }
              }}
              size="xs"
              color="gray"
            >{button.icon}{button.label}</Button>
          :
          null
        ))}
      </div>
    </>
  )

  return (
    <div className={`saved-item relative flex items-start py-1 ${isHovered ? 'bg-gray-50 px-2 -mx-2 rounded' : ''}`} ref={ref}>
      {!isDemo &&
        <DragHandle />
      }
      {allowSelecting && 
        <input
          type="checkbox"
          className="checkbox rounded border-gray-300 mr-2 h-5 w-5 mt-[0.4rem]"
          onClick={(e) => {
            e.stopPropagation();
          }}
          onChange={(e) => toggleSelectItemId(savedItem.id as number)} // to squelch react error msg about not having onchange
          checked={selectedItemIds?.some(id => id === savedItem.id)}
        />
      }     
      {isAccordion
        ?
        <Accordion
          title={''}
          defaultOpen={false}
          theme="no-background"
          wrapperClassName={`flex-grow ${isHovered ? 'opacity-50' : ''}`}
          headerClassName="!pl-0 !mt-0"
          headerContent={
            <div className="flex-grow flex items-center">
              {savedItemContent}
            </div>
          }
        >
          <div className="mt-1 -mb-1 border-t border-gray-200">
            {isDemo ?
              <SavedItemList
                key={JSON.stringify(childItems.map(item => item.id))}
                items={childItems}
                collectionName="savedCases"
                isDemo={isDemo}
                allowSelecting={false}
              />
              :
              <SortableList
                key={JSON.stringify(childItems.map(item => item.id))}
                items={childItems}
                collectionName="savedCases"
                customButtons={[
                  {
                    label: 'Remove from batch',
                    onClick: (onClickItem: ComparisonCase, index: number) => {
                      const oldCaseIds = (savedItem as ComparisonCaseBatch).caseIds.slice();
                       // mutate the oldCasIds array by removing the target element
                      oldCaseIds.splice(index, 1);
                      const newCaseIds = oldCaseIds;
                      db.savedBatches.update(savedItem.id, {caseIds: newCaseIds})
                    }
                  }
                ]}
                allowSelecting={false}
                onSortEnd={(e: {oldIndex: number, newIndex: number}) => {
                  const newItems = arrayMoveImmutable(childItems, e.oldIndex, e.newIndex).map((item, index) => {
                    return {
                      ...item,
                      sortIndex: index
                    }
                  })
                  const caseIds = newItems.map(item => item.id);
                  db.savedBatches.update(savedItem.id, { caseIds });
                  if (setCachedSavedBatches) {
                    setCachedSavedBatches(savedBatches => {
                      const newBatches = [...savedBatches].map(batch => {
                        if (batch.id !== savedItem.id) {
                          return batch;
                        } else {
                          return {
                            ...batch,
                            caseIds
                          }
                        }
                      })
                      return newBatches;
                    })
                  }
                }}
              />
            }
            
          </div>
        </Accordion>
        :
        savedItemContent
      }
      {isHovered &&
        <PlusCircleIcon className="fade-in h-10 w-10 text-green-600 absolute top-1/2 left-1/2 -mt-5 -ml-5" />
      }
    </div>
  )
}

type BatchDropzoneRef = {
  savedBatchId: number;
  ref: React.RefObject<HTMLDivElement>;
  isHovered?: boolean;
}

const SavedCaseBrowserContext = React.createContext({
  cachedSavedCases: [],
  setCachedSavedCases: () => {},
  cachedSavedBatches: [],
  setCachedSavedBatches: () => {},
  demoCases: [],
  demoBatches: [],
  selectedModule: undefined,
  savedBatchDropzoneRefs: [],
  setSavedBatchDropzoneRefs: () => {},
  toggleBatchDropzoneRefHovered: () => {},
} as {
  cachedSavedCases: ComparisonCase[];
  setCachedSavedCases: React.Dispatch<React.SetStateAction<ComparisonCase[]>>
  cachedSavedBatches: ComparisonCaseBatch[];
  setCachedSavedBatches: React.Dispatch<React.SetStateAction<ComparisonCaseBatch[]>>
  demoCases: ComparisonCase[],
  demoBatches: ComparisonCaseBatch[],
  selectedModule: ComparableResultsModuleProps | undefined;
  savedBatchDropzoneRefs: BatchDropzoneRef[];
  setSavedBatchDropzoneRefs: React.Dispatch<React.SetStateAction<BatchDropzoneRef[]>>;
  toggleBatchDropzoneRefHovered: (id: number) => void;
});

const SortableList = SortableContainer(SavedItemList);
const SortableItem = SortableElement(SavedItem);
const DragHandle = SortableHandle(() => (
  <div className="cursor-move text-gray-300 flex -ml-2 mt-1">
    <DotsVerticalIcon className="h-6 w-6 -mr-4"/>
    <DotsVerticalIcon className="h-6 w-6"/>
  </div>
));

export const SavedCaseBrowser = () => {

  const [selectedModuleType, setSelectedModuleType] = React.useState('');

  const selectedModule = comparableResultsModules.find(m => m.type === selectedModuleType);

  const performQueryStringActions = () => {
    const queryString = location.search?.replace('?', '');
    if (queryString) {
      const [action, value] = queryString.split('=');
      if (typeof action === 'undefined' || typeof value === 'undefined') {
        return;
      }
      switch (action) {
        case 'moduleType':
          setSelectedModuleType(value);
          break;
        default:
          break;  
      }
      var cleanURI = location.protocol + "//" + location.host + location.pathname;
      window.history.replaceState({}, document.title, cleanURI);
    }
  }

  React.useEffect(() => {
    performQueryStringActions();
  }, [])

  const savedCases = useLiveQuery(
    async () => {
      if (selectedModuleType) {
        return await db.savedCases.where('type').equals(selectedModuleType).sortBy('sortIndex')
      } else {
        return []
      }
    },
    [selectedModuleType],
    [],
  ) as ComparisonCase[]

  const savedBatches = useLiveQuery(
    async () => {
      if (selectedModuleType) {
        return await db.savedBatches.where('type').equals(selectedModuleType).sortBy('sortIndex')
      } else {
        return []
      }
    },
    [selectedModuleType],
    [],
  ) as ComparisonCaseBatch[]

  // keep locally cached copy of saved cases and batches to prevent jank on dragging and dropping due to delay in updating Dexie store and receiving updates back
  const [cachedSavedCases, setCachedSavedCases] = React.useState(savedCases);
  const [cachedSavedBatches, setCachedSavedBatches] = React.useState(savedBatches);

  React.useEffect(() => {
    setCachedSavedCases(savedCases);
  }, [savedCases]);

  React.useEffect(() => {
    setCachedSavedBatches(savedBatches);
  }, [savedBatches]);

  const [savedBatchDropzoneRefs, setSavedBatchDropzoneRefs] = React.useState<BatchDropzoneRef[]>([]);

  // console.log(savedBatchDropzoneRefs)

  const toggleBatchDropzoneRefHovered = (id: number) => {
    setSavedBatchDropzoneRefs(prevRefs => {
      // if (prevRefs) {
        return [...prevRefs].map(ref => {
          if (ref.savedBatchId !== id) {
            return ref;
          } else {
            return {
              ...ref,
              isHovered: !ref.isHovered
            }
          }
        })
      // }
    })
  }

  React.useEffect(() => {
    setSavedBatchDropzoneRefs(cachedSavedBatches.map(batch => {
      return {savedBatchId: batch.id, ref: React.createRef<HTMLDivElement>()};
    }))
  }, [cachedSavedBatches])

  return (
    <Layout
      title="Saved"
    >
      <SEO title="Saved" />
      <div className="flex h-full flex-col -mb-4">
        <div className="bg-gray-50 py-3 gutter-x -mt-2 border-b border-gray-200 flex items-center">
          <div className="space-x-3">
            {comparableResultsModules.filter(m => m.allowComparisons).map((moduleData, index) => {
              const isSelected = selectedModuleType === moduleData.type;
              return (
                <Button
                  color={isSelected ? 'dark-gray' : 'gray'}
                  key={index}
                  className={`whitespace-nowrap ${false ? '!border !border-blue-500 !text-blue-500' : ''}`}
                  onClick={(e) => {
                    setSelectedModuleType(moduleData.type)
                  }}
                  id={`select-module-${moduleData.type}`}
                >
                  {moduleData.buttonText ?? moduleData.title}
                </Button>
              )
            })}
          </div>
          {!selectedModule &&
            <div className="ml-4 text-emerald-600 font-bold">← Select a module to view saved cases for that module</div>
          }
        </div>
        <SavedCaseBrowserContext.Provider
          value={{
            cachedSavedCases,
            setCachedSavedCases,
            cachedSavedBatches,
            setCachedSavedBatches,
            // demoCases: demoCases.filter(o => o.type === selectedModuleType),
            // demoBatches: demoBatches.filter(o => o.type === selectedModuleType),
            selectedModule,
            savedBatchDropzoneRefs,
            setSavedBatchDropzoneRefs,
            toggleBatchDropzoneRefHovered,
          }}
        >
          <div className="grid grid-cols-2 divide-x flex-grow">
            <SavedItemBlock
              title="Saved Cases"
              collectionName="savedCases"
            />
            <SavedItemBlock
              title="Saved Batches"
              collectionName="savedBatches"
            />
          </div>
          <div className="border-t border-gray-200 grid grid-cols-2 divide-x flex-grow">
            <SavedItemBlock
              title="Demo Cases"
              collectionName="savedCases"
              isDemo={true}
              />
            <SavedItemBlock
              title="Demo Batches"
              collectionName="savedBatches"
              allowDragDrop={false}
              isDemo={true}
            />
          </div>
        </SavedCaseBrowserContext.Provider>
      </div>

    </Layout>
  )
}