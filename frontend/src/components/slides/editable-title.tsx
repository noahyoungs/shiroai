import { useState } from "react";
import { Textarea, Skeleton, Tooltip, input } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { template } from "lodash";
import { cn } from "@/utils/cn";

type EditableTitleProps = {
  title: string;
  onSave: (newTitle: string) => void;
  loading: boolean;
  h1ClassName?: string;
  inputWrapperClassName?: string;
  inputClassName?: string;
};

const minTitleLength = 1;
const maxTitleLength = 80;

export function EditableTitle({
  title,
  onSave,
  loading,
  h1ClassName,
  inputWrapperClassName,
  inputClassName,
}: EditableTitleProps) {
  const [tempTitle, setTempTitle] = useState(title);
  const [editingTitle, setEditingTitle] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveTitle = () => {
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
            <div className="flex flex-row">
              <Tooltip
                content="Clear"
                placement="bottom"
                offset={15}
                color="danger"
              >
                <Icon
                  icon="tabler:circle-x"
                  width="32"
                  height="32"
                  className="text-danger-500 hover:text-danger-600"
                  onClick={() => setTempTitle("")}
                />
              </Tooltip>
              <Tooltip
                content="Revert"
                placement="bottom"
                offset={15}
                color="warning"
              >
                <Icon
                  icon="tabler:circle-chevrons-left"
                  width="32"
                  height="32"
                  className="text-warning-500 hover:text-warning-600"
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
                  width="32"
                  height="32"
                  className="text-success-500 hover:text-success-600"
                  onClick={saveTitle}
                />
              </Tooltip>
            </div>
          }
          placement="left-end"
          offset={15}
          onMouseDown={(e) => e.preventDefault()}
          className="translate-y-2"
        >
          <Textarea
            value={tempTitle}
            onChange={(e) => setTempTitle(e.target.value)}
            onBlur={saveTitle}
            classNames={{
              input: "text-4xl font-bold",
              inputWrapper: "!m-0 !p-0",
              label: "hidden",
              description: "hidden",
              base: "!m-0 !p-0",
              errorMessage: "",
            }}
            variant="underlined"
            autoFocus
            minRows={0}
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
          />
        </Tooltip>
      ) : (
        <Skeleton className="rounded-lg" isLoaded={!loading}>
          <div className="border-b-medium border-transparent rounded-none">
            <div
              className={"pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]"}
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
