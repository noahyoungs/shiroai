// short-bullets-slide-boxes.tsx
import { ShortBulletsSlide, IconData, Slide } from "@shared-utils/database-types";
import { ExcerptCard } from "@/components/excerpt-card";
import { Icon } from "@iconify/react";
import React, { useState, useEffect, useRef } from "react";
import { cn } from "@shared-utils/cn";
import { EditableTitle } from "../editable-title";
import axios from "axios";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Tooltip,
  Textarea,
  Spinner,
  Button,
  Input,
} from "@nextui-org/react";

type BulletItemProps = {
  bullet: any;
  index: number;
  allSources?: any[];
  slide: ShortBulletsSlide;
  saveBulletItemChanges: (
    newText: string,
    newIcon: any,
    index: number,
    deleteSource: boolean
  ) => Promise<void>;
  deleteBulletItem: (index: number) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

const BulletItem: React.FC<BulletItemProps> = ({
  bullet,
  index,
  allSources,
  slide,
  saveBulletItemChanges,
  deleteBulletItem,
  presentationID,
  setBlockArrowKeys,
}) => {
  const [editing, setEditing] = useState(false);
  const [bulletContent, setBulletContent] = useState(bullet.content);
  const [refreshing, setRefreshing] = useState(false);
  const [sourceIconHovered, setSourceIconHovered] = useState(false);
  const [pendingDeleteSource, setPendingDeleteSource] = useState(false);
  const [newIconData, setNewIconData] = useState<IconData | undefined>(
    bullet.icon
  );
  const [previewIcon, setPreviewIcon] = useState<IconData | undefined>(
    bullet.icon
  );
  const [simpleIconOptions, setSimpleIconOptions] = useState<IconData[]>([]);
  const [uniqueIconOptions, setUniqueIconOptions] = useState<IconData[]>([]);
  const [searchIconOptions, setSearchIconOptions] = useState<IconData[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searching, setSearching] = useState(false);
  const bulletRef = useRef<HTMLDivElement>(null);
  const cancelTriggered = useRef(false);

  const handleBlur = async (e: React.FocusEvent) => {
    // if modal is open, clicked inside the element, or editing is already false, DO NOTHING (editing is unchanged)
    if (
      isOpen ||
      e.currentTarget.contains(e.relatedTarget) ||
      editing === false
    ) {
      return;
    }

    // if the revert button was clicked, dont save stuff, but set editing to false
    if (cancelTriggered.current) {
      cancelTriggered.current = false;
      setBulletContent(bullet.content);
      setNewIconData(bullet.icon);
      setPendingDeleteSource(false);
    }
    // only save stuff if the content has changed, the icon has changed, or the delete source button was clicked
    else if (
      bulletContent !== bullet.content ||
      pendingDeleteSource ||
      newIconData?.name !== bullet.icon.name
    ) {
      // SAVING STUFF HERE
      setRefreshing(true);

      // if the content changed, but the icon hasnt changed, find a new icon
      let iconToSet = newIconData;
      if (
        newIconData?.name === bullet.icon.name &&
        bulletContent !== bullet.content
      ) {
        try {
          const response = await axios.post(
            `${process.env.NEXT_PUBLIC_REST_API_URL}/icon/simple_bp_search`,
            {
              bullet_point: bulletContent,
              n: 1,
              presentation_id: presentationID,
            },
            {
              withCredentials: true,
            }
          );
          const iconList = response.data;
          const newIcon = iconList.length > 0 ? iconList[0] : null;
          if (newIcon) {
            iconToSet = newIcon;
            setNewIconData(newIcon);
          }
        } catch (error) {
          console.error("Error fetching icon data:", error);
        }
      }

      await saveBulletItemChanges(
        bulletContent,
        iconToSet,
        index,
        pendingDeleteSource
      );
      setPendingDeleteSource(false);
      setRefreshing(false);
      // END SAVE STUFF
    }

    // set editing to false at the end
    setEditing(false);
    setBlockArrowKeys(false);
  };

  const handleDeleteNode = () => {
    setEditing(false);
    setBlockArrowKeys(false);
    deleteBulletItem(index);
  };

  const handleDeleteSource = () => {
    setPendingDeleteSource(true);
  };

  const handleTextareaClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const handleTooltipClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (editing) {
      handleDeleteSource();
    }
  };

  const handleSearchButtonClick = async () => {
    if (!searchQuery.length) {
      setSearchIconOptions([]);
      return;
    }
    setSearching(true);
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_REST_API_URL}/icon/query_search`,
        {
          query: searchQuery,
          n: 15,
          presentation_id: presentationID,
        },
        {
          withCredentials: true,
        }
      );
      setSearchIconOptions(response.data);
      setSearching(false);
    } catch (error) {
      console.error("Error fetching icons:", error);
      setSearching(false);
    }
  };

  // MODAL
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const fetchIcons = async (bulletContent: string) => {
    try {
      const simpleResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_REST_API_URL}/icon/simple_bp_search`,
        {
          bullet_point: bulletContent,
          n: 10,
          presentation_id: presentationID,
        },
        {
          withCredentials: true,
        }
      );
      setSimpleIconOptions(simpleResponse.data);

      const uniqueResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_REST_API_URL}/icon/unique_bp_search`,
        {
          bullet_point: bulletContent,
          bullet_point_list: slide.slide_content.map(
            (content) => content.content
          ),
          n: 20,
          presentation_id: presentationID,
        },
        {
          withCredentials: true,
        }
      );
      setUniqueIconOptions(uniqueResponse.data);
    } catch (error) {
      console.error("Error fetching icons:", error);
    }
  };

  useEffect(() => {
    if (isOpen) {
      if (!simpleIconOptions.length) {
        fetchIcons(bullet.content);
      }
    }
  }, [isOpen, bullet.content]);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSearchButtonClick();
    }
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        closeButton={<Icon icon="tabler:x" width={40} height={40} />}
        classNames={{
          closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
        }}
        size="5xl"
        scrollBehavior="outside"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-10">
                Select Icon
              </ModalHeader>
              <ModalBody>
                <div className="flex flex-row gap-6 justify-evenly flex-wrap">
                  {/* PREVIEW */}
                  <div>
                    <p className="font-semibold mb-3">Preview</p>
                    <div className="relative flex flex-col items-start bg-background rounded-3xl p-6 w-[18rem] h-[14rem] justify-between border-2 border-foreground">
                      <div className="flex items-center justify-center h-14 w-14 bg-blue-500 rounded-full text-white font-light overflow-hidden flex-shrink-0">
                        <Icon
                          className="text-[33px]"
                          icon={
                            !previewIcon
                              ? "tabler:file-unknown"
                              : previewIcon.source === "fluent"
                              ? `fluent-emoji-high-contrast:${previewIcon.name}`
                              : `tabler:${previewIcon.name}`
                          }
                        />
                      </div>
                      <div className="text-start flex-none">
                        {bullet.content.includes(": ") ? (
                          <>
                            {bullet.content
                              .split(": ")
                              .map((part: string, partIndex: number) => (
                                <p
                                  key={String(partIndex)}
                                  className={cn(
                                    "text-foreground font-[550] overflow-hidden text-ellipsis mb-1",
                                    partIndex === 0
                                      ? "text-lg leading-tight"
                                      : "text-sm font-normal"
                                  )}
                                  style={{
                                    display: "-webkit-box",
                                    WebkitLineClamp: partIndex === 0 ? 2 : 3,
                                    WebkitBoxOrient: "vertical",
                                  }}
                                >
                                  {part.trim()}
                                </p>
                              ))}
                          </>
                        ) : (
                          <p
                            className="text-foreground text-lg font-[550] leading-tight"
                            style={{
                              display: "-webkit-box",
                              WebkitLineClamp: 4,
                              WebkitBoxOrient: "vertical",
                            }}
                          >
                            {bullet.content}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  {/* SUGGESTED */}
                  <div>
                    <p className="font-semibold mb-6 text-left">Suggested</p>
                    {simpleIconOptions.length ? (
                      <div className="grid grid-cols-5 gap-6 w-[261px]">
                        {[
                          ...simpleIconOptions,
                          ...uniqueIconOptions
                            .filter(
                              (uniqueIcon) =>
                                !simpleIconOptions.some(
                                  (simpleIcon) =>
                                    simpleIcon.name === uniqueIcon.name
                                )
                            )
                            .slice(0, 10),
                        ].map((icon) => (
                          <Tooltip content={icon.detailed_name} key={icon.name}>
                            <div
                              className={cn(
                                "flex items-center justify-center rounded-full text-foreground/80 font-light cursor-pointer m-0 p-0 w-[33px] overflow-visible",
                                icon.name === previewIcon?.name &&
                                "ring-[3px] ring-primary ring-offset-4 ring-offset-background text-foreground"
                              )}
                              onClick={() => setPreviewIcon(icon)}
                            >
                              <Icon
                                className="text-[33px]"
                                icon={
                                  icon.source === "fluent"
                                    ? `fluent-emoji-high-contrast:${icon.name}`
                                    : `tabler:${icon.name}`
                                }
                              />
                            </div>
                          </Tooltip>
                        ))}
                      </div>
                    ) : (
                      <div className="w-[261px] h-[204px] flex flex-row justify-center items-start">
                        <Spinner className="" color="primary" size="md" />
                      </div>
                    )}
                  </div>
                  {/* SEARCH */}
                  <div className="w-[261px] h-[147px]">
                    <p className="font-semibold mb-5">Search Icons</p>
                    <div className="flex flex-row mb-5 h-[41px]">
                      <Input
                        aria-label="Search"
                        classNames={{
                          inputWrapper:
                            "bg-content2 dark:bg-content1 h-full rounded-r-none",
                        }}
                        labelPlacement="outside"
                        placeholder="Search..."
                        radius="lg"
                        onValueChange={(value: string) => {
                          setSearchQuery(value);
                        }}
                        value={searchQuery}
                        onKeyDown={handleKeyDown}
                        variant={"faded"}
                      />
                      <Button
                        isIconOnly
                        aria-label="search"
                        color="primary"
                        onPress={handleSearchButtonClick}
                        className="h-full rounded-l-none"
                        isLoading={searching}
                      >
                        <Icon icon="tabler:search" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-5 gap-6">
                      {searchIconOptions.map((icon) => (
                        <Tooltip content={icon.detailed_name} key={icon.name}>
                          <div
                            className={cn(
                              "flex items-center justify-center rounded-full text-foreground/80 font-light cursor-pointer m-0 p-0 w-[33px] overflow-visible",
                              icon.name === previewIcon?.name &&
                                "ring-[3px] ring-primary ring-offset-4 text-foreground"
                            )}
                            onClick={() => setPreviewIcon(icon)}
                          >
                            <Icon
                              className="text-[33px]"
                              icon={
                                icon.source === "fluent"
                                  ? `fluent-emoji-high-contrast:${icon.name}`
                                  : `tabler:${icon.name}`
                              }
                            />
                          </div>
                        </Tooltip>
                      ))}
                    </div>
                  </div>
                </div>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Cancel
                </Button>
                <Button
                  color="primary"
                  onPress={() => {
                    setNewIconData(previewIcon);
                    onClose();
                  }}
                >
                  Save
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>

      <div
        key={index}
        className={cn(
          "relative flex flex-col items-start bg-background rounded-3xl p-6 h-full w-full justify-between",
          editing && "ring-2 ring-foreground"
        )}
        onFocus={() => {
          if (!editing) {
            setEditing(true);
            setBlockArrowKeys(true);
          }
        }}
        onBlur={handleBlur}
        ref={bulletRef}
        tabIndex={0}
      >
        <div
          className="flex items-center justify-center h-14 w-14 bg-blue-500 rounded-full text-white font-light overflow-hidden flex-shrink-0"
          onClick={(e) => {
            e.stopPropagation();
            onOpen();
          }}
        >
          <Icon
            className="text-[33px]"
            icon={
              editing
                ? !newIconData
                  ? "tabler:file-unknown"
                  : newIconData.source === "fluent"
                  ? `fluent-emoji-high-contrast:${newIconData.name}`
                  : `tabler:${newIconData.name}`
                : !bullet.icon
                ? "tabler:file-unknown"
                : bullet.icon.source === "fluent"
                ? `fluent-emoji-high-contrast:${bullet.icon.name}`
                : `tabler:${bullet.icon.name}`
            }
          />
        </div>
        {bullet.excerpt && !pendingDeleteSource && (
          <Tooltip
            content={
              <>
                <div className="flex w-full mb-3 justify-start">
                  <h3 className="text-lg mb-0">Source</h3>
                </div>
                <ExcerptCard
                  text={bullet.excerpt.text}
                  source={allSources?.find(
                    (source) => source.id === bullet.excerpt.source_id
                  )}
                />
              </>
            }
            placement="bottom"
            showArrow
            className="items-start p-4"
          >
            <div
              className={cn(
                "absolute top-4 right-4 cursor-pointer",
                editing ? "text-danger/70 hover:text-danger" : "text-primary"
              )}
              onMouseEnter={() => setSourceIconHovered(true)}
              onMouseLeave={() => setSourceIconHovered(false)}
              onClick={handleTooltipClick}
            >
              <Icon
                icon={editing ? "tabler:input-x" : "tabler:input-search"}
                width="20"
                height="20"
              />
              {editing && sourceIconHovered && (
                <div className="absolute bottom-8 left-1/2 bg-danger text-background text-sm p-2 rounded-medium shadow-small box-border w-auto -translate-x-1/2 whitespace-nowrap z-50">
                  Remove Source
                </div>
              )}
            </div>
          </Tooltip>
        )}
        <div className="text-start flex-none">
          {editing ? (
            <Textarea
              className="text-foreground text-lg font-[550] leading-tight"
              value={bulletContent}
              onChange={(e) => setBulletContent(e.target.value)}
              disableAnimation
              onClick={handleTextareaClick}
              variant="bordered"
              fullWidth
            />
          ) : bullet.content.includes(":") ? (
            <>
              {bullet.content
                .split(":")
                .map((part: string, partIndex: number) => (
                  <p
                    key={String(partIndex)}
                    className={cn(
                      "text-foreground font-[550] overflow-hidden text-ellipsis mb-1",
                      partIndex === 0
                        ? "text-lg leading-tight"
                        : "text-sm font-normal"
                    )}
                    style={{
                      display: "-webkit-box",
                      WebkitLineClamp: partIndex === 0 ? 2 : 3,
                      WebkitBoxOrient: "vertical",
                    }}
                  >
                    {part.trim()}
                  </p>
                ))}
            </>
          ) : (
            <p
              className="text-foreground text-lg font-[550] leading-tight"
              style={{
                display: "-webkit-box",
                WebkitLineClamp: 4,
                WebkitBoxOrient: "vertical",
              }}
            >
              {bullet.content}
            </p>
          )}
          {slide.sequential && index !== slide.slide_content.length - 1 && (
            <div className="absolute top-1/2 -right-8 -translate-y-[16.5px]">
              <Icon
                className="text-[33px] text-foreground/70 "
                icon="tabler:chevron-compact-right"
              />
            </div>
          )}
        </div>
        {refreshing && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/50 rounded-3xl">
            <Spinner color="primary" size="sm" />
          </div>
        )}
        {/* CONTROLS */}
        {editing && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background border-2 border-foreground rounded-xl shadow-md">
            <div className="flex flex-row p-2">
            <Tooltip
                content="Delete"
                placement="top"
                offset={15}
                color="danger"
                isDisabled={slide.slide_content.length <= 2}
              >
                <Icon
                  icon="tabler:circle-x"
                  width="25"
                  height="25"
                  className={cn("text-danger-500 mx-0.5", slide.slide_content.length <= 2 ? "opacity-30" : "hover:text-danger-600")}
                  onClick={handleDeleteNode}
                />
              </Tooltip>
              <Tooltip
                content="Revert"
                placement="top"
                offset={15}
                color="warning"
              >
                <Icon
                  icon="tabler:circle-chevrons-left"
                  width="25"
                  height="25"
                  className="text-warning-500 hover:text-warning-600 mx-0.5"
                  onClick={() => {
                    cancelTriggered.current = true;
                    if (bulletRef.current) {
                      bulletRef.current.blur();
                    }
                  }}
                />
              </Tooltip>
              <Tooltip
                content="Save"
                placement="top"
                offset={15}
                color="success"
              >
                <Icon
                  icon="tabler:circle-check"
                  width="25"
                  height="25"
                  className="text-success-500 hover:text-success-600 mx-0.5"
                  onClick={() => {
                    if (bulletRef.current) {
                      bulletRef.current.blur();
                    }
                  }}
                />
              </Tooltip>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

const renderSlideContent = (
  slide: ShortBulletsSlide,
  allSources: any[] | undefined,
  saveSlideTitle: (newTitle: string) => Promise<void>,
  titleLoading: boolean,
  setBlockArrowKeys: (block: boolean) => void,
  saveBulletItemChanges: (
    newText: string,
    newIcon: any,
    index: number,
    deleteSource: boolean
  ) => Promise<void>,
  deleteBulletItem: (index: number) => void,
  presentationID: string
) => {
  switch (slide.slide_content.length) {
    case 2:
      return (
        <div className="grid grid-rows-2 gap-8 h-full">
          <div className="row-span-1 col-span-full my-auto">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="grid grid-cols-2 gap-8 h-full row-span-1">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.bullet_id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
                saveBulletItemChanges={saveBulletItemChanges}
                deleteBulletItem={deleteBulletItem}
                presentationID={presentationID}
                setBlockArrowKeys={setBlockArrowKeys}
              />
            ))}
          </div>
        </div>
      );
    case 3:
      return (
        <div className="grid grid-rows-2 gap-8 h-full">
          <div className="row-span-1 col-span-full my-auto">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="grid grid-cols-3 gap-8 h-full row-span-1">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.bullet_id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
                saveBulletItemChanges={saveBulletItemChanges}
                deleteBulletItem={deleteBulletItem}
                presentationID={presentationID}
                setBlockArrowKeys={setBlockArrowKeys}
              />
            ))}
          </div>
        </div>
      );
    case 4:
      return (
        <div className="grid grid-cols-3 gap-8 h-full">
          <div className="col-span-1 flex flex-col justify-center">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="col-span-2 grid grid-cols-2 grid-rows-2 gap-8">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.bullet_id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
                saveBulletItemChanges={saveBulletItemChanges}
                deleteBulletItem={deleteBulletItem}
                presentationID={presentationID}
                setBlockArrowKeys={setBlockArrowKeys}
              />
            ))}
          </div>
        </div>
      );
    case 5:
      return (
        <div className="grid grid-rows-2 grid-cols-3 gap-8 h-full">
          <div className="col-span-1 row-span-1 my-auto">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          {slide.slide_content.map((bullet, index) => (
            <BulletItem
              key={bullet.bullet_id}
              bullet={bullet}
              index={index}
              allSources={allSources}
              slide={slide}
              saveBulletItemChanges={saveBulletItemChanges}
              deleteBulletItem={deleteBulletItem}
              presentationID={presentationID}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          ))}
        </div>
      );
    default:
      return null;
  }
};

type ShortBulletsSlideComponentProps = {
  presentationID: string;
  slide: ShortBulletsSlide;
  setSlide: (slide: Partial<Slide>) => void;
  allSources?: any[];
  setBlockArrowKeys: (block: boolean) => void;
};

export const BoxesShortBulletsSlideComponent: React.FC<
  ShortBulletsSlideComponentProps
> = ({ presentationID, slide, setSlide, allSources, setBlockArrowKeys }) => {
  const testSlideContent = slide.slide_content.slice(0, 5);

  const [titleLoading, setTitleLoading] = useState(false);


  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    setSlide({
      slide_title: newTitle,
    });
    setTitleLoading(false);
  };

  const saveBulletItemChanges = async (
    newText: string,
    newIcon: IconData | undefined,
    index: number,
    deleteSource: boolean
  ) => {
    console.log(
      "Saving bullet item changes, new text:",
      newText,
      "new icon:",
      newIcon,
      "index:",
      index,
      "delete source:",
      deleteSource
    );
    const newSlideContent = slide.slide_content.map((bullet: any, i: number) =>
      i === index
        ? {
            ...bullet,
            content: newText,
            icon: newIcon ? newIcon : bullet.icon,
            excerpt: deleteSource ? null : bullet.excerpt,
          }
        : bullet
    );
    await setSlide({
      slide_content: newSlideContent,
    });
  };

  const deleteBulletItem = async (index: number) => {
    console.log("Deleting bullet at index", index);
    // ensure that there are at least 2 bullets
    if (slide.slide_content.length <= 2) {
      alert("Must have at least 2 nodes");
      return;
    }
    const newSlideContent = slide.slide_content.filter(
      (bullet: any, i: number) => i !== index
    );
    console.log("Before update", slide.slide_content);
    console.log("After update", newSlideContent);
    setSlide({
      slide_content: newSlideContent,
    });
    console.log("After fetchslide", slide.slide_content);
  };

  console.log("Component mount, Slide content", slide.slide_content);

  return (
    <div className="p-12 flex flex-col relative height-auto w-full flex-grow">
      <div className="flex justify-center w-full h-full">
        {renderSlideContent(
          { ...slide, slide_content: testSlideContent },
          allSources,
          saveSlideTitle,
          titleLoading,
          setBlockArrowKeys,
          saveBulletItemChanges,
          deleteBulletItem,
          presentationID
        )}
      </div>
    </div>
  );
};
