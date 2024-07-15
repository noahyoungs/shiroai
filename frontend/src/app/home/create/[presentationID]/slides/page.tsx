//page.tsx
"use client";

import { Chat } from "@/components/chat/chat";
import Interface from "./interface";
import { Tabs, Tab, Card, CardBody } from "@nextui-org/react";
import { useEffect, useState, useRef, useCallback } from "react";
import { io } from "socket.io-client";
import { useRouter } from "next/navigation";
import ChatConfigureLayout from "@/components/chat-configure-layout";
import { PersistentSlideList } from "@/utils/persistent-slides-list";
import { getSources } from "@/actions/slides-actions";
import debounce from "lodash/debounce";

export default function Page({
  params,
}: {
  params: { presentationID: string };
}) {
  const redirectPath = `/home/create/${params.presentationID}/export`;
  const interface_name = "slides";
  console.log(`presentationID: ${params.presentationID}`);

  const [messages, setMessages] = useState<any[]>([]);
  const socketRef = useRef<any>(null);
  const [blockChat, setBlockChat] = useState<boolean>(false);
  // const [typing, setTyping] = useState<boolean>(false);

  // Interface states
  const [currentSlideID, setCurrentSlideID] = useState<string | null>(null);
  const [allSources, setAllSources] = useState<any[]>([]);
  const [pushingSlideStatus, setPushingSlideStatus] = useState<{
    [key: string]: string;
  }>({});
  const [fetchingSlideStatus, setFetchingSlideStatus] = useState<{
    [key: string]: string;
  }>({});
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const router = useRouter();

  // Define functions to update state
  const updatePushingSlideStatus = (id: string, status: string) => {
    setPushingSlideStatus((oldStatus) => ({ ...oldStatus, [id]: status }));
  };

  const updateErrors = (id: string, error: string) => {
    setErrors((oldErrors) => ({ ...oldErrors, [id]: error }));
  };

  const sendInterfaceUpdate = (slideIDs: string | string[]) => {
    console.log("Sending interface update push request:", slideIDs);
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit("interface_update", {
        push: slideIDs,
      });
    } else {
      console.error("Socket not connected");
    }
  };

  // Initialize PersistentSlideList with update functions
  const [slideList] = useState(
    new PersistentSlideList(
      params.presentationID,
      updatePushingSlideStatus,
      updateErrors,
      sendInterfaceUpdate
    )
  );

  useEffect(() => {
    const newSocket = io("http://localhost:8000", {
      withCredentials: true,
      query: {
        presentationID: params.presentationID,
        interface_name,
      },
    });

    socketRef.current = newSocket;
    console.log("Connected to websocket");

    newSocket.on("connect", () => {
      console.log("Socket connected");
    });

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
          // setTyping(false);
        }
        // if (socketMessage.role === "user") {
        //   setTyping(true);
        // }
      } else {
        console.error("Received invalid message from socket: ", socketMessage);
      }
    });

    newSocket.on("replace_message", (socketMessage: any) => {
      console.log("Received replace message ", socketMessage);
      if (typeof socketMessage === "object") {
        if (socketMessage.role === "assistant") {
          setMessages((prevMessages: any[]) => {
            const newMessages = [...prevMessages];
            newMessages.pop();
            return [...newMessages, socketMessage];
          });
        } else {
          console.error(
            "Received non assistant replace message from socket: ",
            socketMessage
          );
        }
      } else {
        console.error(
          "Received invalid replace message from socket: ",
          socketMessage
        );
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
      if (socketMessage.push) {
        if (socketMessage.push == "*") {
          await fetchAllSlides();
        } else if (
          (Array.isArray(socketMessage.push) &&
            socketMessage.push.length > 0 &&
            socketMessage.push.every(
              (slideid: any) => typeof slideid === "string"
            )) ||
          typeof socketMessage.push === "string"
        ) {
          await fetchSlides(socketMessage.push);
        } else {
          console.error(
            "Invalid push value in interface update:",
            socketMessage.push
          );
        }
      }

      if (socketMessage.current_slide_id) {
        if (!(typeof socketMessage.current_slide_id === "string")) {
          console.error(
            "Invalid current slide id in interface update:",
            socketMessage.current_slide_id
          );
        }
        if (!slideList.getSlide(socketMessage.current_slide_id)) {
          console.error(
            "Invalid current slide id in interface update:",
            socketMessage.current_slide_id
          );
        }
        setCurrentSlideID(socketMessage.current_slide_id);
      }
    });

    newSocket.on("proceed", (socketMessage: any) => {
      console.log("Proceeding to next step:", socketMessage);
      newSocket.disconnect();
      setBlockChat(true);
      router.push(redirectPath);
    });

    newSocket.on("update_complete", (socketMessage: any) => {
      console.log("Update complete:", socketMessage);
      if (socketMessage.status === "success") {
        if (Array.isArray(socketMessage.slide_ids)) {
          setPushingSlideStatus((prevStatus) => {
            const newStatus = { ...prevStatus };
            socketMessage.slide_ids.forEach((slideID: string) => {
              delete newStatus[slideID];
            });
            return newStatus;
          });
          console.log("Done pushing slides:", socketMessage.slide_ids);
        } else if (typeof socketMessage.slide_ids === "string") {
          setPushingSlideStatus((prevStatus) => {
            const newStatus = { ...prevStatus };
            delete newStatus[socketMessage.slide_ids];
            return newStatus;
          });
          console.log("Done pushing slide:", socketMessage.slide_ids);
        } else {
          console.error("Invalid slide_ids in update complete:", socketMessage);
        }
      } else if (socketMessage.status === "error") {
        if (Array.isArray(socketMessage.slide_ids)) {
          socketMessage.slide_ids.forEach((slideID: string) => {
            updateErrors(slideID, socketMessage.error);
          });
        } else if (typeof socketMessage.slide_id === "string") {
          updateErrors(socketMessage.slide_id, socketMessage.error);
        } else {
          console.error("Invalid slide_ids in update complete:", socketMessage);
        }
      } else {
        console.error("Invalid status in update complete:", socketMessage);
      }
    });

    initialize();

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const debouncedEmitInterfaceUpdate = useCallback(
    debounce((currentSlideID: string) => {
      if (socketRef.current && socketRef.current.connected && currentSlideID) {
        socketRef.current.emit("interface_update", {
          current_slide_id: currentSlideID,
        });
      }
    }, 300), // Adjust the debounce delay as needed
    []
  );

  // Send to socket when current slide id changes
  useEffect(() => {
    if (currentSlideID) {
      debouncedEmitInterfaceUpdate(currentSlideID);
    }
  }, [currentSlideID, debouncedEmitInterfaceUpdate]);

  const fetchAllSlides = async () => {
    await slideList.fetchAllSlides();
    slideList.length && setCurrentSlideID(slideList.getHeadSlideID());
  };

  const initialize = async () => {
    const sources = await getSources(params.presentationID);
    sources && setAllSources(sources);
    await fetchAllSlides();
  };

  const fetchSlides = async (slideIDs: string | string[]) => {
    // console.log("Fetching slide(s):", slideIDs);
    // set status to 'fetching'
    if (Array.isArray(slideIDs)) {
      console.log("fetching slides", slideIDs);
      slideIDs.forEach((slideID) => {
        setFetchingSlideStatus((prevStatus) => ({
          ...prevStatus,
          [slideID]: "fetching",
        }));
      });
    }
    if (typeof slideIDs === "string") {
      console.log("fetching slide", slideIDs);
      setFetchingSlideStatus((prevStatus) => ({
        ...prevStatus,
        [slideIDs]: "fetching",
      }));
    }

    slideList.fetchSlides(slideIDs);

    // delete the status
    if (Array.isArray(slideIDs)) {
      slideIDs.forEach((slideID) => {
        setFetchingSlideStatus((prevStatus) => {
          const newStatus = { ...prevStatus };
          delete newStatus[slideID];
          return newStatus;
        });
      });
    } else if (typeof slideIDs === "string") {
      setFetchingSlideStatus((prevStatus) => {
        const newStatus = { ...prevStatus };
        delete newStatus[slideIDs];
        return newStatus;
      });
    }
  };

  // get all slides in the beginning
  useEffect(() => {
    initialize();
  }, []);

  const chat = (
    <Chat
      presentationID={params.presentationID}
      messages={messages}
      setMessages={setMessages}
      socket={socketRef.current}
      block={
        blockChat ||
        !socketRef.current?.connected ||
        Object.keys(pushingSlideStatus).length > 0 ||
        Object.keys(fetchingSlideStatus).length > 0
      }
      setBlock={setBlockChat}
      typing={messages.at(-1)?.role === "user"}
      statusMessage={
        currentSlideID && messages.at(-1)?.role !== "user"
          ? `I see you're now viewing the slide titled *${
              slideList.getSlide(currentSlideID)?.slide_title
            }*. Let me know if I can change anything on this slide for you.`
          : undefined
      }
    />
  );

  const interfaceComponent = (
    <Interface
      slideList={slideList}
      currentSlideID={currentSlideID}
      setCurrentSlideID={setCurrentSlideID}
      allSources={allSources}
      presentationID={params.presentationID}
      pushingSlideStatus={pushingSlideStatus}
      fetchingSlideStatus={fetchingSlideStatus}
      errors={errors}
      socketReady={socketRef.current && socketRef.current.connected}
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
