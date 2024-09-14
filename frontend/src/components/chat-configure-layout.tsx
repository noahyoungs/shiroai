"use client"

import { ReactNode, useEffect, useState } from 'react';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@shared-utils/cn";

type ChatConfigureLayoutProps = {
    chat: ReactNode;
    interfaceComponent: ReactNode;
    thirds?: boolean;
};

export default function ChatConfigureLayout({ chat, interfaceComponent, thirds=false }: ChatConfigureLayoutProps) {
    const [isWideScreen, setIsWideScreen] = useState(false);
    const [activeTab, setActiveTab] = useState("chat");

    // Resize event listener for chat and interface responsive layout
    useEffect(() => {
        const handleResize = () => {
            setIsWideScreen(window.innerWidth >= 1280);
        };

        handleResize();

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return (
        <>
            {isWideScreen ? (
                <div className="flex flex-row h-screen w-screen">
                    <div className={cn("pl-[1.5%] pr-[0.75%]", thirds? "w-[33.2vw]" : "w-1/2")}>
                        {chat}
                    </div>
                    <div className={cn("pl-[0.75%] pr-[1.5%]", thirds? "w-[66.5vw]" : "w-1/2")}>
                        {interfaceComponent}
                    </div>
                </div>
            ) : (
                <div className="flex flex-col h-screen w-screen">
                    {/* Tab container */}
                    <div className="flex-none">
                        <Tabs
                            size="lg"
                            fullWidth
                            classNames={{
                                base: "box-border",
                                tabList: "flex flex-none",
                            }}
                            // @ts-ignore
                            onSelectionChange={(key) => setActiveTab(key)}
                        >
                            <Tab
                                key="chat"
                                title={
                                    <div className="flex items-center space-x-2 box-border">
                                        <Icon icon="tabler:message-chatbot" height={24} width={24} />
                                        <span>Chat</span>
                                    </div>
                                }
                            >
                            </Tab>
                            <Tab
                                key="interface"
                                title={
                                    <div className="flex items-center space-x-2 box-border">
                                        <Icon icon="tabler:tool" height={24} width={24} />
                                        <span>Configure</span>
                                    </div>
                                }
                            >
                            </Tab>
                        </Tabs>
                    </div>

                    {/* Panel container */}
                    <div className="flex-grow overflow-y-auto px-[2%]">
                        {activeTab === "chat" ? chat : interfaceComponent}
                    </div>
                </div>
            )}
        </>
    );
}