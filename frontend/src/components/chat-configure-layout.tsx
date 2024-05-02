"use client"

import { ReactNode, useEffect, useState } from 'react';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";

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
                <div className="flex flex-row h-screen w-screen px-8">
                    <div className={cn("pr-4", thirds? "w-1/3" : "w-1/2")}>
                        {chat}
                    </div>
                    <div className={cn("pl-4", thirds? "w-2/3" : "w-1/2")}>
                        {interfaceComponent}
                    </div>
                </div>
            ) : (
                <div className="flex flex-col h-screen w-screen sm:px-8">
                    {/* Tab container */}
                    <div className="flex-none">
                        <Tabs
                            size="lg"
                            fullWidth
                            classNames={{
                                base: "",
                                tabList: "flex flex-none",
                            }}
                            // @ts-ignore
                            onSelectionChange={(key) => setActiveTab(key)}
                        >
                            <Tab
                                key="chat"
                                title={
                                    <div className="flex items-center space-x-2">
                                        <Icon icon="tabler:message-chatbot" height={24} width={24} />
                                        <span>Chat</span>
                                    </div>
                                }
                            >
                            </Tab>
                            <Tab
                                key="interface"
                                title={
                                    <div className="flex items-center space-x-2">
                                        <Icon icon="tabler:tool" height={24} width={24} />
                                        <span>Configure</span>
                                    </div>
                                }
                            >
                            </Tab>
                        </Tabs>
                    </div>

                    {/* Panel container */}
                    <div className="flex-grow overflow-y-auto">
                        {activeTab === "chat" ? chat : interfaceComponent}
                    </div>
                </div>
            )}
        </>
    );
}