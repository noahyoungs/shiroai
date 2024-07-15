// page.tsx
"use client"

import { Chat } from '@/components/chat/chat';
import Interface from './interface';
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { useEffect, useState, useCallback } from 'react';
import { io } from "socket.io-client";
import { useRouter } from 'next/navigation';
import ChatConfigureLayout from '@/components/chat-configure-layout';
import { debounce } from 'lodash';


export default function Page({ params }: { params: { presentationID: string } }) {
  const redirectPath = `/home/create/${params.presentationID}/slides`;

  const interface_name = "outline";
  console.log(`presentationID: ${params.presentationID}`);

  const [messages, setMessages] = useState<any[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [blockChat, setBlockChat] = useState<boolean>(false);
  const [blockInterface, setBlockInterface] = useState<boolean>(true);

  // Interface states
  const [allTopics, setAllTopics] = useState<any[]>(["loading"]);
  const [includedTopics, setIncludedTopics] = useState<any[]>([]);
  const [excludedTopics, setExcludedTopics] = useState<any[]>([]);

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
    
      if (socketMessage.all_topics && socketMessage.outline && socketMessage.all_topics.length !== socketMessage.outline.length) {
        throw new Error(`Received inconsistent interface update from socket: ${socketMessage}`);
      }
      if (socketMessage.all_topics && socketMessage.all_topics.length > 0) {
        console.log("Setting all topics", socketMessage.all_topics);
        setAllTopics(socketMessage.all_topics);
      } else {
        console.log("all_topics not present or has length 0 in socketMessage:", socketMessage);
      }
    
      let referenceTopics = socketMessage.all_topics || allTopics;
      console.log("referenceTopics:", referenceTopics);
    
      if (socketMessage.outline) {
        const includedTopics = [];
        const excludedTopics = [];
    
        socketMessage.outline.forEach(subtopic => {
          const topic = referenceTopics.find(topic => topic.id === subtopic.id);
          if (topic) {
            if (subtopic.included) {
              includedTopics.push(topic);
            } else {
              excludedTopics.push(topic);
            }
          }
        });
    
        if (includedTopics.length + excludedTopics.length !== socketMessage.outline.length) {
          console.error("Mismatched ids", { socket: socketMessage.all_topics, memory: allTopics, outline: socketMessage.outline });
        }
    
        console.log("includedTopics:", includedTopics);
        console.log("excludedTopics:", excludedTopics);
    
        setIncludedTopics(includedTopics);
        setExcludedTopics(excludedTopics);
      } else {
        console.log("outline not present in socketMessage:", socketMessage);
      }
    
      setBlockInterface(false);
    });

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
    const outline = [...includedTopics.map(topic => ({ id: topic.id, included: true })), ...excludedTopics.map(topic => ({ id: topic.id, included: false }))]
    if (outline.length === 0) {
      console.error("Not emitting interface update because outline is empty")
      return;
    }
    console.log("Emitting interface update", { outline })
    emitInterfaceUpdate({ outline: outline});
  }, [includedTopics, excludedTopics, emitInterfaceUpdate]);


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
    includedTopics={includedTopics}
    setIncludedTopics={setIncludedTopics}
    excludedTopics={excludedTopics}
    setExcludedTopics={setExcludedTopics}
    block={blockInterface || blockChat}
    presentationID={params.presentationID}
    redirectPath={redirectPath}
   />;

  return (
    <ChatConfigureLayout chat={chat} interfaceComponent={interfaceComponent} />
  );
}