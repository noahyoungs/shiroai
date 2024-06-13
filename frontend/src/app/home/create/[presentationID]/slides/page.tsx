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
import { getSlides, getSources, getSlide } from "@/actions/slides-actions";
import { Slide } from "@/utils/slide-types";

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
  const [slides, setSlides] = useState<Slide[]>([]);
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

    newSocket.on("interface_update", (socketMessage: any) => {
      console.log("Received interface update:", socketMessage);
      if (socketMessage.push == "all_slides") {
        const fetchAllSlides = async () => {
          const slides = await getSlides(params.presentationID);
          slides && setSlides(slides);
          slides.length && setCurrentSlideID(slides[0].id);
        };

        fetchAllSlides();
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

  async function sortSlides(slides: Slide[]) {
    return slides.sort((a, b) => a.slide_order - b.slide_order);
  }

  const initialize = async () => {
    let slides = await getSlides(params.presentationID);
    const sources = await getSources(params.presentationID);
    if (slides) {
      // remove slides where .hidden is true
      slides = slides.filter((slide) => !slide.hidden);
    }
    slides && sortSlides(slides);
    slides && setSlides(slides);
    sources && setAllSources(sources);
    slides.length && setCurrentSlideID(slides[0].id);
  };
  
  const fetchSlide = async (slideID: string) => {
    const newSlides = await getSlide(params.presentationID, slideID);
  
    if (newSlides && newSlides.length > 0) {
      setSlides((prevSlides) => {
        // Filter out hidden new slides from the newSlides array
        const visibleNewSlides = newSlides.filter(slide => !slide.hidden);
  
        // Remove slides from the previous state if their id matches any hidden slides from newSlides
        const updatedPrevSlides = prevSlides.filter(prevSlide => {
          const hiddenSlide = newSlides.find(newSlide => newSlide.id === prevSlide.id && newSlide.hidden);
          return !hiddenSlide;
        });
  
        if (visibleNewSlides.length === 1) {
          return updatedPrevSlides.map((slide) => {
            if (slide.id === visibleNewSlides[0].id) {
              return visibleNewSlides[0];
            }
            return slide;
          });
        } else if (visibleNewSlides.length > 1) {
          const updatedSlides = [...updatedPrevSlides];
          const index = updatedSlides.findIndex((slide) => slide.id === slideID);
  
          if (index !== -1) {
            updatedSlides.splice(index, 1, ...visibleNewSlides);
          } else {
            console.warn("Slide not found in the existing slides array");
          }
  
          return updatedSlides;
        } else {
          return updatedPrevSlides;
        }
      });
    } else {
      console.error("Failed to fetch slide with ID", slideID);
    }
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
      slides={slides}
      currentSlideID={currentSlideID}
      setCurrentSlideID={setCurrentSlideID}
      allSources={allSources}
      block={blockInterface || blockChat}
      presentationID={params.presentationID}
      redirectPath={redirectPath}
      fetchSlide={fetchSlide}
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
