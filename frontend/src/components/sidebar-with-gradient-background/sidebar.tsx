"use client";

import React from "react";
import {Avatar, Button, ScrollShadow, Spacer, Input, useDisclosure} from "@nextui-org/react";
import {Icon} from "@iconify/react";

import {AcmeLogo} from "./acme";
import SidebarDrawer from "./sidebar-drawer";
import { signOut, useSession } from 'next-auth/react';
import ThemeSwitch from "../theme-switch";


export default function Component({
  children,
  nav,
  title = "Overview",
}: {
  children?: React.ReactNode;
  nav?: React.ReactNode;
  title?: string;
}) {
  const {isOpen, onOpen, onOpenChange} = useDisclosure();

  const { data: session } = useSession();

  const content = (
    <div className="relative flex h-full w-72 flex-1 flex-col bg-gradient-to-b from-default-100 via-danger-100 to-secondary-100 p-6">
      <div className="flex items-center gap-2 px-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-full border-small border-foreground/20">
          <AcmeLogo className="text-foreground" />
        </div>
        <span className="text-small font-medium text-foreground">Shiro AI</span>
      </div>

      <Spacer y={4} />
      <h3 className="mb-0">Presentations</h3>

      <ScrollShadow className="-mr-6 h-full max-h-full py-3 pr-6">
        {nav}
      </ScrollShadow>

      <Spacer y={8} />

      <div className="mt-auto flex flex-col">
        {/* Profile */}
        <div className="flex items-center gap-3 px-2">
        <Avatar size="sm" src={session?.user?.image || ""} />
          <div className="flex flex-col">
            <p className="text-small text-foreground">{session?.user?.email}</p>
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
          className="justify-start text-foreground/80 data-[hover=true]:text-foreground"
          startContent={
            <Icon
              className="text-foreground -translate-x-0.5"
              icon="tabler:logout-2"
              width={24}
            />
          }
          variant="light"
          onClick={() => signOut()}
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
      <div className="flex w-full flex-col gap-y-4 p-4 sm:max-w-[calc(100%_-_288px)]">

            <Button
              isIconOnly
              className="flex sm:hidden"
              size="sm"
              variant="light"
              onPress={onOpen}
            >
              <Icon
                className="text-default-500"
                height={24}
                icon="solar:hamburger-menu-outline"
                width={24}
              />
            </Button>

        <main className="flex h-full">
          <div className="flex h-full w-full flex-col gap-4 rounded-medium border-small border-divider p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
