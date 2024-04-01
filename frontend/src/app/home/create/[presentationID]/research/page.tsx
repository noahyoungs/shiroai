// page.tsx
"use client"

import { Chat } from '@/components/chat/chat';
import Interface from './interface';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { useEffect, useState, useCallback } from 'react';
import { io } from "socket.io-client";
import { useRouter } from 'next/navigation';
import MainStructure from '@/components/main-structure';


export default function Page({ params }: { params: { presentationID: string } }) {
  const redirectPath = `/home/create/${params.presentationID}/outline`;

  const interface_name = "research";
  console.log(`presentationID: ${params.presentationID}`);

  const [isWideScreen, setIsWideScreen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [blockChat, setBlockChat] = useState<boolean>(false);
  const [blockInterface, setBlockInterface] = useState<boolean>(true);
  const [typing, setTyping] = useState<boolean>(false);

  // Interface states
  const [sources, setSources] = useState<any[]>([]);
  const [sourcesLoading, setSourcesLoading] = useState(false);

  const router = useRouter();
  // Socket connection, handle received messages
  useEffect(() => {
    const newSocket = io("http://localhost:8000", {
      withCredentials: true,
      query: {
        presentationID: params.presentationID,
        interface_name,
      },
    });

    setSocket(newSocket);
    console.log("Connected to websocket");

    newSocket.on("initMessages", (socketMessage: any) => {
      console.log("Received init messages ", socketMessage);
      if (Array.isArray(socketMessage)) {
        setMessages(socketMessage);
      } else {
        console.error("Received invalid init messages from socket: ", socketMessage);
      }
    });

    newSocket.on("message", (socketMessage: any) => {
      console.log("Received socket message ", socketMessage);
      if (typeof socketMessage === "object") {
        setMessages((prevMessages: any[]) => [...prevMessages, socketMessage]);
        if (socketMessage.role === "assistant" ){
          setBlockChat(false);
          setTyping(false);
        }
        if (socketMessage.role === "user"){
          setTyping(true);
        }
      } else {
        console.error("Received invalid message from socket: ", socketMessage);
      }
    });

    newSocket.on('disconnect_request', (socketMessage: any) => {
      console.log('Disconnect reason:', socketMessage.reason);
      setMessages([{ role: 'error', content: socketMessage.reason }]);
      newSocket.disconnect();
      setBlockChat(true);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from websocket");
    });

    newSocket.on('interface_update', (socketMessage: any) => {
      console.log('Received interface update:', socketMessage);
      setSources(socketMessage.sources);
      setBlockInterface(false);
      setSourcesLoading(false);
    }
    );

    newSocket.on('proceed', (socketMessage: any) => {
      console.log('Proceeding to next step:', socketMessage);
      newSocket.disconnect();
      setBlockChat(true);
      setBlockInterface(true);
      router.push(redirectPath);
    }
    );

    return () => {
      newSocket.disconnect();
    };
  }, []);


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

  const refreshSources = useCallback(() => {
    if (socket) {
      setSourcesLoading(true);
      socket.emit("interface_update", {action: "refresh"});
    }
  }, [socket]);

  const deleteSource = useCallback((id: string) => {
    if (socket) {
      socket.emit("interface_update", {action: "delete", id: id});
      setSourcesLoading(true);
    }
  }, [socket]);

  const chat = <Chat
    presentationID={params.presentationID}
    messages={messages}
    socket={socket}
    block={blockChat}
    setBlock={setBlockChat}
    typing={typing}
    sources={sources}
    refreshSources={refreshSources}
  />;

  const interfaceComponent = <Interface
    sources={sources}
    block={blockInterface || blockChat}
    presentationID={params.presentationID}
    refreshSources={refreshSources}
    deleteSource={deleteSource}
    sourcesLoading={sourcesLoading}
    redirectPath={redirectPath}
   />;

  return (
    <MainStructure chat={chat} interfaceComponent={interfaceComponent} />
  );
}