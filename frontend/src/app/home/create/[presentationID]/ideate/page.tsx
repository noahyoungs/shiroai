// page.tsx
"use client"

import { Chat } from '@/components/chat/chat';
import Interface from './interface';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { useEffect, useState, useCallback } from 'react';
import { io } from "socket.io-client";
import { debounce } from 'lodash';
import { useRouter } from 'next/navigation';
import ChatConfigureLayout from '@/components/chat-configure-layout';
import { env } from 'process';

export default function Page({ params }: { params: { presentationID: string } }) {
  const interfaceName = "ideate";
  const redirectPath = `/home/create/${params.presentationID}/research`;
  console.log(`presentationID: ${params.presentationID}`);

  const [messages, setMessages] = useState<any[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [blockChat, setBlockChat] = useState<boolean>(false);
  const [blockInterface, setBlockInterface] = useState<boolean>(true);

  // Interface states
  const [topic, setTopic] = useState<string>("");
  const [audience, setAudience] = useState<string>("");
  const [goal, setGoal] = useState<string>("");

  const router = useRouter();

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!backendUrl) {
    throw new Error("Backend URL not set");
  }

  // Socket connection, handle received messages
  useEffect(() => {
    const newSocket = io(backendUrl, {
      withCredentials: true,
      query: {
        presentationID: params.presentationID,
        interface_name: interfaceName,
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
      setTopic(socketMessage.topic);
      setAudience(socketMessage.audience);
      setGoal(socketMessage.goal);
      setBlockInterface(false);
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

  // Send to socket when interface states change
  const emitInterfaceUpdate = useCallback(
    debounce((data) => {
      if (socket) {
        socket.emit("interface_update", data);
      }
    }, 500),
    [socket]
  );

  useEffect(() => {
    emitInterfaceUpdate({ topic, audience, goal });
  }, [topic, audience, goal, emitInterfaceUpdate]);

  
  const chat = <Chat
    presentationID={params.presentationID}
    messages={messages}
    setMessages={setMessages}
    socket={socket}
    block={blockChat}
    setBlock={setBlockChat}
    typing={messages.at(-1)?.role === "user"}
  />;

  const interfaceComponent = <Interface
    topic={topic}
    audience={audience}
    goal={goal}
    setTopic={setTopic}
    setAudience={setAudience}
    setGoal={setGoal}
    block={blockInterface || blockChat}
    redirectPath={redirectPath}
    presentationID={params.presentationID}
   />;

  return (
    <ChatConfigureLayout chat={chat} interfaceComponent={interfaceComponent} />
  );
}