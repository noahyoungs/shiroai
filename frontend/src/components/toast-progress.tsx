import { CircularProgress } from "@nextui-org/react";
import { Icon } from "@iconify/react";
type ToastProgressProps = {
  progress_value: number;
  message: string;
};

export function ToastProgress({ progress_value, message }: ToastProgressProps) {
  return (
    <>
      <div className="flex flex-row items-center w-full h-full gap-4">
        <CircularProgress
          aria-label="Loading..."
          size="lg"
          value={progress_value}
          valueLabel={
            progress_value >= 100 ? (
              <Icon icon="line-md:confirm" width={20} className="text-success"/>
            ) : null
          }
          color={progress_value >= 100 ? "success" : "primary"}
          showValueLabel={progress_value >= 100}
        />
        <p className="text-center text-base">{message}</p>
      </div>
    </>
  );
}
