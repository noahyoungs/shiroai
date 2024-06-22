// page.tsx
"use client";

import { Chat } from "@/components/chat/chat";
import Interface from "./interface";
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { useEffect, useState, useCallback } from "react";
import { io } from "socket.io-client";
import { useRouter } from "next/navigation";
import ChatConfigureLayout from "@/components/chat-configure-layout";
import { debounce, set } from "lodash";
import { Slide } from "@/utils/slide-types";
import { PersistentSlideList } from "@/utils/persistent-slides-list";
import { getSources } from "@/actions/slides-actions";

export default function Page({
  params,
}: {
  params: { presentationID: string };
}) {
  const redirectPath = `/home/create/${params.presentationID}/export`;

  const interface_name = "slides";
  console.log(`presentationID: ${params.presentationID}`);

  const [messages, setMessages] = useState<any[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [blockChat, setBlockChat] = useState<boolean>(false);
  const [blockInterface, setBlockInterface] = useState<boolean>(true);
  const [typing, setTyping] = useState<boolean>(false);

  // Interface states
  const [slideList, _ ] = useState(new PersistentSlideList(params.presentationID));
  const [currentSlideID, setCurrentSlideID] = useState<string | null>(null);
  const [allSources, setAllSources] = useState<any[]>([]);

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
        console.error(
          "Received invalid init messages from socket: ",
          socketMessage
        );
      }
    });

    newSocket.on("message", (socketMessage: any) => {
      console.log("Received socket message ", socketMessage);
      if (typeof socketMessage === "object") {
        setMessages((prevMessages: any[]) => [...prevMessages, socketMessage]);
        if (socketMessage.role === "assistant") {
          setBlockChat(false);
          setTyping(false);
        }
        if (socketMessage.role === "user") {
          setTyping(true);
        }
      } else {
        console.error("Received invalid message from socket: ", socketMessage);
      }
    });

    newSocket.on("disconnect_request", (socketMessage: any) => {
      console.log("Disconnect reason:", socketMessage.reason);
      setMessages([{ role: "error", content: socketMessage.reason }]);
      newSocket.disconnect();
      setBlockChat(true);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from websocket");
    });

    newSocket.on("interface_update", async (socketMessage: any) => {
      console.log("Received interface update:", socketMessage);
      if (socketMessage.push == "all_slides") {
        await fetchAllSlides();
      }
      setBlockInterface(false);
    });

    newSocket.on("proceed", (socketMessage: any) => {
      console.log("Proceeding to next step:", socketMessage);
      newSocket.disconnect();
      setBlockChat(true);
      setBlockInterface(true);
      router.push(redirectPath);
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  // // Send to socket when interface states change
  // const emitInterfaceUpdate = useCallback(
  //   debounce((data) => {
  //     if (socket) {
  //       socket.emit("interface_update", data);
  //     }
  //   }, 500),
  //   [socket]
  // );

  // useEffect(() => {
  //   const outline = [...includedTopics.map(topic => ({ id: topic.id, included: true })), ...excludedTopics.map(topic => ({ id: topic.id, included: false }))]
  //   if (outline.length === 0) {
  //     console.error("Not emitting interface update because outline is empty")
  //     return;
  //   }
  //   console.log("Emitting interface update", { outline })
  //   emitInterfaceUpdate({ outline: outline});
  // }, [includedTopics, excludedTopics, emitInterfaceUpdate]);

  const fetchAllSlides = async () => {
    await slideList.fetchAllSlides();
    slideList.length && setCurrentSlideID(slideList.getHeadSlideID());
  }

  const initialize = async () => {
    const sources = await getSources(params.presentationID);
    sources && setAllSources(sources);
    await fetchAllSlides();
  };

  const fetchSlide = async (slideID: string) => {
    // slideList.fetchSlide(slideID);
    slideList.getSlide(slideID);
  };

  // get all slides in the begining
  useEffect(() => {
    initialize();
  }, []);

  const chat = (
    <Chat
      presentationID={params.presentationID}
      messages={messages}
      socket={socket}
      block={blockChat}
      setBlock={setBlockChat}
      typing={typing}
    />
  );

  const interfaceComponent = (
    <Interface
      slideList={slideList}
      currentSlideID={currentSlideID}
      setCurrentSlideID={setCurrentSlideID}
      allSources={allSources}
      block={blockInterface || blockChat}
      presentationID={params.presentationID}
      redirectPath={redirectPath}
    />
  );

  return (
    <ChatConfigureLayout
      chat={chat}
      interfaceComponent={interfaceComponent}
      thirds
    />
  );
}
