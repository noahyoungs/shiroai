"use client";

import type { RadioGroupProps, RadioProps } from "@nextui-org/react";
import React from "react";
import {
  RadioGroup,
  VisuallyHidden,
  useRadio,
  useRadioGroupContext,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { useTheme } from "next-themes";
import { cn } from "@shared-utils/cn";

const ThemeRadioItem = ({
  icon,
  ...props
}: RadioProps & { icon: string }) => {
  const { theme, setTheme } = useTheme();
  const {
    Component,
    isSelected: isSelfSelected,
    getBaseProps,
    getInputProps,
    getWrapperProps,
  } = useRadio(props);
  const groupContext = useRadioGroupContext();
  const isSelected =
    isSelfSelected ||
    String(groupContext.groupState.selectedValue) === String(props.value) ||
    theme === props.value;

  const wrapperProps = getWrapperProps();

  const handleClick = () => {
    setTheme(props.value);
  };

  return (
    <Component {...getBaseProps()} onClick={handleClick}>
      <VisuallyHidden>
        <input {...getInputProps()} />
      </VisuallyHidden>
      <div
        {...wrapperProps}
        className={cn(
          wrapperProps?.["className"],
          "pointer-events-none h-8 w-8 rounded-full border-black border-opacity-10 ring-0 transition-transform group-data-[pressed=true]:scale-90",
          {
            "bg-foreground/30": isSelected,
          }
        )}
      >
        <Icon className="text-foreground/80" icon={icon} width={18} />
      </div>
    </Component>
  );
};

const ThemeSwitch = React.forwardRef<
  HTMLDivElement,
  Omit<RadioGroupProps, "children">
>(({ classNames = {}, ...props }, ref) => {
  const { theme } = useTheme();

  return (
    <RadioGroup
      ref={ref}
      aria-label="Select a theme"
      classNames={{
        ...classNames,
        wrapper: cn("gap-1 items-center", classNames?.wrapper),
      }}
      defaultValue={theme}
      orientation="horizontal"
      {...props}
    >
      <ThemeRadioItem icon="tabler:moon" value="dark" />
      <ThemeRadioItem icon="tabler:sun-moon" value="system" />
      <ThemeRadioItem icon="tabler:sun-high" value="light" />
    </RadioGroup>
  );
});

ThemeSwitch.displayName = "ThemeSwitch";

export default ThemeSwitch;