"use client";

import React from "react";
import { Avatar, Link, Button, ScrollShadow, Spacer, Input, useDisclosure } from "@nextui-org/react";
import CreatePresentation from "@/actions/create-presentation";

import { Icon } from "@iconify/react";
import { AcmeLogo } from "./acme";
import SidebarDrawer from "./sidebar-drawer";
import { useSession } from 'next-auth/react';
import ThemeSwitch from "../theme-switch";
import { cn } from "@/utils/cn";


export default function Component({
  children,
  list,
  title = "Overview",
}: {
  children?: React.ReactNode;
  list?: React.ReactNode;
  title?: string;
}) {
  const { isOpen, onOpen, onClose, onOpenChange } = useDisclosure();
  const { data: session } = useSession();

  const content = (
    <div className="relative flex h-full w-72 flex-1 flex-col bg-gradient-to-b from-default-100 via-danger-100 to-secondary-100 p-6">
      <div className="flex flex-row justify-between">
        <div className="flex items-center gap-2 px-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full border-small border-foreground/20">
            <AcmeLogo className="text-foreground" />
          </div>
          <span className="text-small font-medium text-foreground">Shiro AI</span>
        </div>

        <Button
          isIconOnly
          className={cn("flex")}
          size="sm"
          variant="light"
          onPress={onClose}
        >
          <Icon
            className="text-foreground/70 hover:text-foreground"
            height={32}
            icon="tabler:layout-sidebar-left-collapse-filled"
            width={32}
          />
        </Button>
      </div>

      <Spacer y={4} />
      <div className="flex flex-row justify-between">
        <h3 className="mb-0">Presentations</h3>
        <Icon
          icon="tabler:square-plus"
          width={29}
          height={29}
          onClick={async () => {
            const uuid = await CreatePresentation()
            onClose()
          }}
          className="text-foreground/70 hover:text-foreground mr-[2px]"
        />
      </div>

      <ScrollShadow
        className="-mr-6 h-full max-h-full py-3 pr-6"
      >
        {list}
      </ScrollShadow>

      <Spacer y={8} />

      <div className="mt-auto flex flex-col">
        {/* Profile */}
        <div className="flex items-center gap-3 px-2">
          <Avatar
            size="md"
            src={session?.user?.image || undefined}
            name={session?.user?.name || undefined}
            className="flex-none"
          />
          <div className="flex flex-col max-w-[80%]">
            <p className="text-small text-primary-foreground truncate">
              {session?.user?.name || 'Not logged in'}
            </p>
            <p className="text-tiny text-primary-foreground/60 truncate">
              {session?.user?.email || ""}
            </p>
          </div>
        </div>
        <Spacer y={3} />
        <Button
          fullWidth
          className="justify-start text-foreground/80 data-[hover=true]:text-foreground"
          startContent={
            <Icon className="text-foreground" icon="tabler-info-circle" width={24} />
          }
          variant="light"
        >
          Help & Information
        </Button>
        <Button
          href={`https://auth.meetshiro.com/logout?client_id=${encodeURIComponent(process.env.NEXT_PUBLIC_COGNITO_ID)}&logout_uri=${encodeURIComponent(`${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/signout`)}`}
          as={Link}
          className="justify-start logout-button"
          startContent={
            <Icon
              className="text-foreground -translate-x-0.5"
              icon="tabler:logout-2"
              width={24}
            />
          }
          variant="light"
        >
          Log Out
        </Button>
        <Spacer y={4} />
        <div className="flex justify-center">
          <ThemeSwitch />
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-dvh w-full">
      <SidebarDrawer className="flex-none" isOpen={isOpen} onOpenChange={onOpenChange}>
        {content}
      </SidebarDrawer>
      <div>
        <Button
          isIconOnly
          className={cn("flex fixed z-[500] mt-3 ml-3 bg-background", (isOpen && "hidden"))}
          size="sm"
          variant="light"
          onPress={onOpen}
        >
          <Icon
            className="text-foreground/70 hover:text-foreground"
            height={32}
            icon="tabler:layout-sidebar-left-expand-filled"
            // icon="tabler:menu-2"
            width={32}
          />
        </Button>
        {children}
      </div>
    </div>
  );
}
