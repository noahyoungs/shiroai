// short-bullets-slide-pills.tsx
import { ShortBulletsSlide, IconData, Slide } from "@shared-utils/database-types";
import { ExcerptCard } from "@/components/excerpt-card";
import { Icon } from "@iconify/react";
import React, { useState, useRef, useEffect } from "react";
import { cn } from "@shared-utils/cn";
import { EditableTitle } from "../editable-title";
import axios from "axios";
import {
  Tooltip,
  Textarea,
  Spinner,
  Button,
  Input,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@nextui-org/react";

type ShortBulletsSlideComponentProps = {
  presentationID: string;
  slide: ShortBulletsSlide;
  setSlide: (slide: Partial<Slide>) => void;
  allSources?: any[];
  setBlockArrowKeys: (block: boolean) => void;
};

type BulletItemProps = {
  content: string;
  excerptText?: string | null;
  source?: any;
  icon: IconData;
  chevron?: boolean;
  allBulletsShort?: boolean;
  saveBulletItemChanges: (
    newText: string,
    newIcon: IconData | undefined,
    index: number,
    deleteSource: boolean
  ) => Promise<void>;
  deleteBulletItem: (index: number) => void;
  index: number;
  presentationID: string;
  slide: ShortBulletsSlide;
  setBlockArrowKeys: (block: boolean) => void;
};
const BulletItem: React.FC<BulletItemProps> = ({
  content,
  excerptText,
  source,
  icon,
  chevron,
  allBulletsShort,
  saveBulletItemChanges,
  deleteBulletItem,
  index,
  presentationID,
  slide,
  setBlockArrowKeys,
}) => {
  const [editing, setEditing] = useState(false);
  const [bulletContent, setBulletContent] = useState(content);
  const [refreshing, setRefreshing] = useState(false);
  const [sourceIconHovered, setSourceIconHovered] = useState(false);
  const [pendingDeleteSource, setPendingDeleteSource] = useState(false);
  const [newIconData, setNewIconData] = useState<IconData | undefined>(icon);
  const [previewIcon, setPreviewIcon] = useState<IconData | undefined>(icon);
  const [simpleIconOptions, setSimpleIconOptions] = useState<IconData[]>([]);
  const [uniqueIconOptions, setUniqueIconOptions] = useState<IconData[]>([]);
  const [searchIconOptions, setSearchIconOptions] = useState<IconData[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searching, setSearching] = useState(false);
  const bulletRef = useRef<HTMLLIElement>(null);
  const cancelTriggered = useRef(false);

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
      setBulletContent(content);
      setNewIconData(icon);
      setPendingDeleteSource(false);
    }
    // only save stuff if the content has changed, the icon has changed, or the delete source button was clicked
    else if (
      bulletContent !== content ||
      pendingDeleteSource ||
      newIconData?.name !== icon.name
    ) {
      // SAVING STUFF HERE
      setRefreshing(true);

      // if the content changed, but the icon hasnt changed, find a new icon
      let iconToSet = newIconData;
      if (
        newIconData?.name === icon.name &&
        bulletContent !== content
      ) {
        try {
          const response = await axios.post(
            `${process.env.NEXT_PUBLIC_REST_API_URL}/simple_bp_search`,
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

  const handleTextareaClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const handleTooltipClick = () => {
    if (editing) {
      setPendingDeleteSource(true);
    }
  };

  const handleDeleteNode = () => {
    setEditing(false);
    setBlockArrowKeys(false);
    deleteBulletItem(index);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSearchButtonClick();
    }
  };

  useEffect(() => {
    if (isOpen) {
      if (!simpleIconOptions.length) {
        fetchIcons(content);
      }
    }
  }, [isOpen, content]);

  return (
    <li
      ref={bulletRef}
      onFocus={() => {
        if (!editing) {
          setEditing(true);
          setBlockArrowKeys(true);
        }
      }}
      onBlur={handleBlur}
      tabIndex={0}
      className="relative"
    >
      <Modal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        closeButton={<Icon icon="tabler:x" width={40} height={40} />}
        classNames={{
          closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
        }}
        size="2xl"
        scrollBehavior="outside"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-10">
                Select Icon
              </ModalHeader>
              <ModalBody>
                {/* PREVIEW */}
                <div className="mb-6">
                  <p className="font-semibold mb-3">Preview</p>
                  <div className="bg-background rounded-full py-1.5 pl-1.5 pr-6 border-2 border-foreground max-w-max">
                    <div className="flex flex-row items-center">
                      <div className="flex flex-none items-center justify-center h-12 w-12 bg-blue-500 rounded-full text-white font-light overflow-hidden cursor-pointer">
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

                      <div className="text-foreground pl-4 text-base font-[550]">
                        {bulletContent}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex flex-row gap-12 justify-start flex-wrap h-[280px]">
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
                    <p className="font-semibold mb-5">Search</p>
                    <div className="flex flex-row mb-5 h-[41px]">
                      <Input
                        aria-label="Search"
                        classNames={{
                          inputWrapper:
                            "bg-content2 dark:bg-content1 h-[37px] rounded-r-none",
                        }}
                        labelPlacement="outside"
                        placeholder="Search..."
                        radius="lg"
                        onValueChange={(value: string) => {
                          setSearchQuery(value);
                        }}
                        value={searchQuery}
                        onKeyDown={handleKeyDown}
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
        className={cn(
          "flex items-center justify-between bg-background rounded-full py-1.5 pl-1.5 pr-6",
          editing && "ring-2 ring-foreground"
        )}
      >
        <div className="flex flex-row flex-grow items-center">
          {/* CIRCLE */}
          <div
            className="flex flex-none items-center justify-center h-12 w-12 bg-blue-500 rounded-full text-white font-light overflow-hidden cursor-pointer"
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
                  : !icon
                  ? "tabler:file-unknown"
                  : icon.source === "fluent"
                  ? `fluent-emoji-high-contrast:${icon.name}`
                  : `tabler:${icon.name}`
              }
            />
          </div>
          {editing ? (
            <Textarea
              className="text-foreground pl-4 text-base font-[550]"
              value={bulletContent}
              onChange={(e) => setBulletContent(e.target.value)}
              disableAnimation
              onClick={handleTextareaClick}
              style={{ height: "auto" }}
              minRows={0}
              fullWidth
            />
          ) : (
            <span className="text-foreground pl-4 text-base font-[550]">
              {bulletContent}
            </span>
          )}
        </div>
        {source && excerptText && !pendingDeleteSource && (
          <Tooltip
            content={<ExcerptCard text={excerptText} source={source} />}
            placement="bottom"
            showArrow
            className="items-start p-4"
          >
            <div
              className={cn(
                "inline-block ml-2 cursor-pointer",
                editing ? "text-danger" : "text-primary"
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
              {/* REMOVE SOURCE TOOLTIP */}
              {editing && sourceIconHovered && (
                <div className="absolute bottom-12 right-8 translate-x-1/2 bg-danger text-background text-sm p-2 rounded-medium shadow-small box-border w-auto whitespace-nowrap z-50">
                  Remove Source
                </div>
              )}
            </div>
          </Tooltip>
        )}
      </div>
      {/* ARROW */}
      {chevron && (
        <div
          className={cn("absolute -translate-y-1", "right-1/2 translate-x-1/2")}
        >
          <Icon
            icon="tabler:chevron-compact-down"
            className="text-foreground/60 text-[33px]"
          />
        </div>
      )}
      {refreshing && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/50 rounded-full">
          <Spinner color="primary" size="sm" />
        </div>
      )}
      {/* CONTROLS */}
      {editing && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-3/4 bg-background border-2 border-foreground rounded-xl shadow-md">
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
    </li>
  );
};

export function PillShortBulletsSlideComponent({
  presentationID,
  slide,
  setSlide,
  allSources,
  setBlockArrowKeys,
}: ShortBulletsSlideComponentProps) {
  const [titleLoading, setTitleLoading] = useState(false);

  // for title
  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    setSlide( {
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
    const newSlideContent = slide.slide_content.map((bullet, i) =>
      i === index
        ? {
            ...bullet,
            content: newText,
            icon: newIcon ? newIcon : bullet.icon,
            excerpt: deleteSource ? null : bullet.excerpt,
          }
        : bullet
    );
    setSlide({
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
    // console.log("Before update", slide.slide_content);
    // console.log("After update", newSlideContent);
    setSlide({
      slide_content: newSlideContent,
    });
    // console.log("After fetchslide", slide.slide_content);
  };


  const allBulletsShort = slide.slide_content.every(
    (bullet) => bullet.content.length <= 50
  );

  console.log(`"All bullets are short: ${allBulletsShort}`);


  return (
    <div className="p-12 w-full flex-grow flex flex-col">
      {allBulletsShort ? (
        <div className="flex flex-row w-full h-full px-24">
          <div className="w-1/3 flex flex-col items-end justify-center">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="w-2/3 flex justify-end flex-grow">
            <ul className="flex flex-col justify-center gap-6 h-full max-w-max">
              {slide.slide_content.map((bullet, index) => (
                <React.Fragment key={bullet.bullet_id}>
                  <BulletItem
                    content={bullet.content}
                    excerptText={bullet.excerpt && bullet.excerpt.text}
                    source={
                      allSources &&
                      bullet.excerpt &&
                      allSources.find(
                        (source) => source.id === bullet.excerpt?.source_id
                      )
                    }
                    icon={bullet.icon}
                    chevron={
                      slide.sequential &&
                      index != slide.slide_content.length - 1
                    }
                    allBulletsShort={allBulletsShort}
                    saveBulletItemChanges={saveBulletItemChanges}
                    deleteBulletItem={deleteBulletItem}
                    index={index}
                    presentationID={presentationID}
                    slide={slide}
                    setBlockArrowKeys={setBlockArrowKeys}
                  />
                </React.Fragment>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-none w-full">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlideTitle}
              loading={titleLoading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="flex justify-center w-full flex-grow">
            <ul className="flex flex-col justify-evenly gap-6 max-w-max my-8">
              {slide.slide_content.map((bullet, index) => (
                <React.Fragment key={bullet.bullet_id}>
                  <BulletItem
                    content={bullet.content}
                    excerptText={bullet.excerpt?.text}
                    source={
                      allSources &&
                      allSources.find(
                        (source) => source.id === bullet.excerpt?.source_id
                      )
                    }
                    icon={bullet.icon}
                    chevron={
                      slide.sequential &&
                      index != slide.slide_content.length - 1
                    }
                    allBulletsShort={allBulletsShort}
                    saveBulletItemChanges={saveBulletItemChanges}
                    deleteBulletItem={deleteBulletItem}
                    index={index}
                    presentationID={presentationID}
                    slide={slide}
                    setBlockArrowKeys={setBlockArrowKeys}
                  />
                </React.Fragment>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
