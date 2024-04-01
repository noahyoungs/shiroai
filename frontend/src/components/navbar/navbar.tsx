"use client";

import React from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenu,
  NavbarMenuItem,
  NavbarMenuToggle,
  Link,
  Button,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Avatar,
  Breadcrumbs,
  BreadcrumbItem,
  Badge,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";

import { AcmeIcon } from "./social";

import NotificationsCard from "./notifications-card";
import { useTheme } from 'next-themes';
import { signOut, useSession } from 'next-auth/react';
import Cookies from 'js-cookie';
import NextLink from 'next/link';

function logout() {
  Object.keys(Cookies.get()).forEach(cookieName => {
    Cookies.remove(cookieName);
  });
  signOut();
}

export default function NavBar() {

  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const { data: session } = useSession();

  return (
    <div className="w-full">
      <Navbar
        classNames={{
          base: "bg-primary",
          wrapper: "px-4 sm:px-6",
          item: "data-[active=true]:text-primary",
        }}
        height="64px"
      >
        <NavbarBrand className="text-primary-foreground">
          <NavbarMenuToggle className=" h-6 sm:hidden" />
          <NextLink href="/">
            <AcmeIcon />
          </NextLink>
          <NextLink href="/">
            <p className="font-bold text-inherit ml-2">AI Presenter</p>
          </NextLink>
        </NavbarBrand>
        {/* <NavbarContent
          className="ml-4 hidden h-12 w-full max-w-fit gap-4 rounded-full bg-primary-400 px-4 dark:bg-primary-300 sm:flex text-primary-foreground"
          justify="start"
        >
          <NavbarItem isActive>
            <Link className="flex gap-2 text-inherit" href="#">
              Dashboard
            </Link>
          </NavbarItem>
          <NavbarItem>
            <Link aria-current="page" className="flex gap-2 text-inherit" href="#">
              Deployments
            </Link>
          </NavbarItem>
          <NavbarItem>
            <Link className="flex gap-2 text-inherit" href="#">
              Analytics
            </Link>
          </NavbarItem>
          <NavbarItem>
            <Link className="flex gap-2 text-inherit" href="#">
              Team
            </Link>
          </NavbarItem>
        </NavbarContent> */}
        {/* Right Menu */}
        <NavbarContent className="ml-auto h-12 max-w-fit items-center gap-0 text-white" justify="end">
          {/* Theme change */}
          <NavbarItem className="flex">
            <Button isIconOnly radius="full" variant="light" onClick={toggleTheme}>
              <Icon className="text-primary-foreground hidden dark:block" icon="tabler:sun-high" width={24} />
              <Icon className="text-primary-foreground dark:hidden" icon="tabler:moon" width={24} />
            </Button>
          </NavbarItem>
          {/* Settings */}
          {/* <NavbarItem className="hidden lg:flex">
            <Button isIconOnly radius="full" variant="light">
              <Icon
                className="text-primary-foreground"
                icon="solar:settings-linear"
                width={24}
              />
            </Button>
          </NavbarItem> */}
          {/* Notifications */}
          {/* <NavbarItem className="hidden lg:flex">
            <Popover offset={12} placement="bottom-end">
              <PopoverTrigger>
                <Button
                  disableRipple
                  isIconOnly
                  className="overflow-visible"
                  radius="full"
                  variant="light"
                >
                  <Badge color="danger" content="5" showOutline={false} size="md">
                    <Icon
                      className="text-primary-foreground"
                      icon="solar:bell-linear"
                      width={22}
                    />
                  </Badge>
                </Button>
              </PopoverTrigger>
              <PopoverContent className="max-w-[90vw] p-0 sm:max-w-[380px]">
                <NotificationsCard className="w-full shadow-none" />
              </PopoverContent>
            </Popover>
          </NavbarItem> */}
          {/* User Menu */}
          <NavbarItem className="px-2">
            <Dropdown placement="bottom-end">
              <DropdownTrigger>
                <button className="mt-1 h-8 w-8 transition-transform">
                  <Badge
                    classNames={{
                      badge: "border-primary",
                    }}
                    color="success"
                    content=""
                    placement="bottom-right"
                    shape="circle"
                  >
                    <Avatar size="sm" src={session?.user?.image || ""} />
                  </Badge>
                </button>
              </DropdownTrigger>
              <DropdownMenu aria-label="Profile Actions" variant="flat">
                <DropdownItem key="profile" className="h-14 gap-2">
                  <p className="font-semibold">Signed in as</p>
                  <p className="font-semibold">{session?.user?.email}</p>
                </DropdownItem>
                {/* <DropdownItem key="settings">My Settings</DropdownItem>
                <DropdownItem key="team_settings">Team Settings</DropdownItem>
                <DropdownItem key="analytics">Analytics</DropdownItem>
                <DropdownItem key="system">System</DropdownItem>
                <DropdownItem key="configurations">Configurations</DropdownItem>
                <DropdownItem key="help_and_feedback">Help & Feedback</DropdownItem> */}
                <DropdownItem key="logout" color="danger" onClick={() => logout()}>
                  Log Out
                </DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </NavbarItem>
        </NavbarContent>

        {/* Mobile Menu */}
        <NavbarMenu>
          <NavbarMenuItem>
            <Link className="w-full" color="foreground" href="#">
              Dashboard
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem isActive>
            <Link aria-current="page" className="w-full" color="primary" href="#">
              Deployments
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem>
            <Link className="w-full" color="foreground" href="#">
              Analytics
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem>
            <Link className="w-full" color="foreground" href="#">
              Team
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem>
            <Link className="w-full" color="foreground" href="#">
              Settings
            </Link>
          </NavbarMenuItem>
        </NavbarMenu>
      </Navbar>
    </div>
  );
}
