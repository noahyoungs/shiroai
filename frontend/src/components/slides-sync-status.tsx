import { Tooltip, Card, CardBody } from "@nextui-org/react";
import { Icon } from "@iconify/react";

interface SlidesSyncStatusProps {
  pushingSlideStatus: { [key: string]: string };
  fetchingSlideStatus: { [key: string]: string };
  errors: { [key: string]: string };
}

export const SlidesSyncStatus: React.FC<SlidesSyncStatusProps> = ({
  pushingSlideStatus,
  fetchingSlideStatus,
  errors,
}) => {
  const errorCount = Object.keys(errors).length;
  const pushingCount = Object.keys(pushingSlideStatus).length;
  const fetchingCount = Object.keys(fetchingSlideStatus).length;

  const getTooltipContent = () => {
    if (errorCount > 0) {
      return (
        <>
          <p>{errorCount} error{errorCount > 1 ? 's' : ''} arose while synchronizing slides:</p>
          <ol>
            {Object.entries(errors).map(([id, error]) => (
              <li key={id}>Slide {error}</li>
            ))}
          </ol>
        </>
      );
    }

    const actionMap = {
      pushing: { verb: "Uploading", count: pushingCount },
      fetching: { verb: "Downloading", count: fetchingCount },
    };

    const action = pushingCount > 0 ? "pushing" : fetchingCount > 0 ? "fetching" : null;

    return action 
      ? <p>{actionMap[action].verb} {actionMap[action].count} slide{actionMap[action].count > 1 ? 's' : ''}</p>
      : <p>Slides are in sync</p>;
  };

  const getIconProps = () => {
    if (errorCount > 0) {
      return { icon: "tabler:cloud-x", className: "text-danger/70 hover:text-danger" };
    }
    if (pushingCount > 0) {
      return { icon: "tabler:cloud-up", className: "text-primary/70 hover:text-primary animate-pulse" };
    }
    if (fetchingCount > 0) {
      return { icon: "tabler:cloud-down", className: "text-primary/70 hover:text-primary animate-pulse" };
    }
    return { icon: "tabler:cloud-check", className: "text-success" };
  };

  const getColor = () => {
    if (errorCount > 0) {
      return "danger";
    }
    if (pushingCount > 0 || fetchingCount > 0) {
      return "primary";
    }
    return "success";
  }

  return (
    <div className="flex flex-row gap-2 justify-start items-center">
      <Tooltip content={getTooltipContent()} placement="right" color={getColor()}>
        <Icon width={30} {...getIconProps()} />
      </Tooltip>
    </div>
  );
};