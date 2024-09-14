//editable-title.tsx
import { useState, useEffect } from "react";
import { Textarea, Skeleton, Tooltip, input } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { template } from "lodash";
import { cn } from "@shared-utils/cn";

type EditableTitleProps = {
  title: string;
  onSave: (newTitle: string) => void;
  loading: boolean;
  setBlockArrowKeys: (block: boolean) => void;
  classNames? : string;
};

const minTitleLength = 1;
const maxTitleLength = 80;

export function EditableTitle({
  title,
  onSave,
  loading,
  setBlockArrowKeys,
  classNames,
}: EditableTitleProps) {

  // console.log(`Title: ${title}`)

  const [tempTitle, setTempTitle] = useState(title);

  // console.log(`Temp Title: ${tempTitle}`)
  const [editingTitle, setEditingTitle] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setBlockArrowKeys(editingTitle);
  }, [editingTitle, setBlockArrowKeys]);

  useEffect(() => {
    setTempTitle(title);
  }, [title]);

  const saveTitle = () => {
    if (tempTitle === title) {
      setEditingTitle(false);
      return;
    }
    if (
      tempTitle.length >= minTitleLength &&
      tempTitle.length <= maxTitleLength
    ) {
      setEditingTitle(false);
      setError(null);
      onSave(tempTitle);
    } else {
      setError("Title must be between 1 and 50 characters long.");
    }
  };

  return (
    <>
      {editingTitle ? (
        <Tooltip
          isOpen={true}
          content={
            <div className="flex flex-row py-1">
              <Tooltip
                content="Revert"
                placement="bottom"
                offset={15}
                color="warning"
              >
                <Icon
                  icon="tabler:circle-chevrons-left"
                  width="25"
                  height="25"
                  className="text-warning-500 hover:text-warning-600 mx-0.5"
                  onClick={() => {
                    setTempTitle(title);
                    setEditingTitle(false);
                  }}
                />
              </Tooltip>
              <Tooltip
                content="Save"
                placement="bottom"
                offset={15}
                color="success"
              >
                <Icon
                  icon="tabler:circle-check"
                  width="25"
                  height="25"
                  className="text-success-500 hover:text-success-600 mx-0.5"
                  onClick={saveTitle}
                />
              </Tooltip>
            </div>
          }
          placement="left-end"
          offset={15}
          onMouseDown={(e) => e.preventDefault()}
          className="border-2 border-foreground"
        >
          <Textarea
            value={tempTitle}
            onChange={(e) => setTempTitle(e.target.value)}
            onBlur={saveTitle}
            classNames={{
              input: cn("text-4xl font-bold", classNames),
              inputWrapper: "!m-0 !p-0",
              label: "hidden",
              description: "hidden",
              base: "!m-0 !p-0",
              errorMessage: "",
            }}
            variant="underlined"
            autoFocus
            minRows={1}
            disableAnimation
            isInvalid={
              tempTitle.length < minTitleLength ||
              tempTitle.length > maxTitleLength
            }
            errorMessage={
              tempTitle.length < minTitleLength ||
              (tempTitle.length > maxTitleLength &&
                `Must be 1-80 characters long. (Length: ${tempTitle.length})`)
            }
            fullWidth
          />
        </Tooltip>
      ) : (
        <Skeleton className="rounded-lg" isLoaded={!loading}>
          <div className="border-b-medium border-transparent rounded-none">
            <div
              className={cn("pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]" , classNames)}
              onClick={() => setEditingTitle(true)}
            >
              {title}
            </div>
          </div>
        </Skeleton>
      )}
    </>
  );
}
