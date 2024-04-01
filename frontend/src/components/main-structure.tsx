"use client"
import { ReactNode, useEffect, useState } from 'react';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";

type MainStructureProps = {
    chat: ReactNode;
    interfaceComponent: ReactNode;
};

export default function MainStructure({ chat, interfaceComponent }: MainStructureProps) {

    const [isWideScreen, setIsWideScreen] = useState(false);

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
            <div className="flex">
              <div className="w-1/2 mr-5">
                <Card>
                  <CardBody>
                    {chat}
                  </CardBody>
                </Card>
              </div>
              <div className="w-1/2">
                <Card>
                  <CardBody>
                    {interfaceComponent}
                  </CardBody>
                </Card>
              </div>
            </div>
          ) : (
            <Tabs size="lg" aria-label="Options">
              <Tab key="interface" title="Chat">
                <Card>
                  <CardBody>
                    {chat}
                  </CardBody>
                </Card>
              </Tab>
              <Tab key="chat" title="Configure">
                <Card>
                  <CardBody>
                    {interfaceComponent}
                  </CardBody>
                </Card>
              </Tab>
            </Tabs>
          )}
        </>
      );
}

