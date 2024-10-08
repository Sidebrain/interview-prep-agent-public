"use client";
import React, { useState, useRef, useEffect, use } from "react";
import useWebSocket from "@/app/hooks/useWebsocket";
import clientLogger from "@/app/lib/clientLogger";
import UserInputInterface from "./UserInputInterface";
import {
  WebSocketMessage,
  WebsocketMessageZodType,
} from "@/types/websocketTypes";
import { debounce } from "lodash";

const ChatInterfaceHeader = () => {
  return (
    <header className="border border-gray-200 bg-slate-100 rounded-sm items-center justify-center flex text-gray-800 p-4 h-8 ">
      <h1 className="text-md text-center">Header</h1>
    </header>
  );
};

const ChatInterface = () => {
  const { connectionStatus, readyState, sendMessage, msgList, dispatch } =
    useWebSocket({
      url: process.env.NEXT_PUBLIC_WS_URL as string,
    });
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [maxTextareaHeight, setMaxTextareaHeight] = useState<number>(150);

  // clientLogger.debug(connectionStatus, readyState, sendMessage);

  // bring the last message into the view
  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(scrollToBottom, [msgList]);

  // identify the max textarea height
  useEffect(() => {
    function computeMaxHeight() {
      if (containerRef.current) {
        const containerHeight = containerRef.current.clientHeight;
        const newMaxHeight = Math.max(50, Math.max(150, containerHeight * 0.7));
        setMaxTextareaHeight(newMaxHeight);
      }
    }
    computeMaxHeight();
    window.addEventListener("resize", computeMaxHeight);

    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  // useEffect(() => {
  //   if (lastMessage) {
  //     // updateMessageState(lastMessage);
  //     updateMessageState(lastMessage);
  //   }
  // }, [lastMessage]);

  // function updateMessageState(newMessage: WebSocketMessage) {
  //   setMessages((prevMessages) => {
  //     if (newMessage.index < 10) clientLogger.debug(newMessage);
  //     const lastMessage = prevMessages[prevMessages.length - 1];

  //     if (newMessage.type === "chunk" || newMessage.type === "complete") {
  //       if (lastMessage && lastMessage.id === newMessage.id) {
  //         clientLogger.debug(newMessage.index);
  //         // Update existing message
  //         const updatedMessages = [...prevMessages];
  //         updatedMessages[updatedMessages.length - 1] = {
  //           ...lastMessage,
  //           content: (lastMessage.content || "") + (newMessage.content || ""),
  //           type: newMessage.type,
  //         };
  //         return updatedMessages;
  //       } else {
  //         // Add new message
  //         return [...prevMessages, newMessage];
  //       }
  //     }

  //     return prevMessages;
  //   });
  // }
  // function updateMessageState() {
  //   if (!lastMessage) return;
  //   const newMessage = WebsocketMessageZodType.parse(lastMessage);
  //   const debouncedSetMessages = debounce(setMessages, 200);
  //   // clientLogger.debug("New message: ", newMessage);
  //   debouncedSetMessages((prevMsg) => {
  //     const lastReceivedMessage = prevMsg[prevMsg.length - 1];
  //     switch (newMessage.type) {
  //       case "complete":
  //       case "chunk":
  //         // if lastmessage is a chunk or complete type and has same id as last received message
  //         // it means we are receiving the same message in chunks
  //         // clientLogger.debug(lastReceivedMessage.content, newMessage.content);
  //         const accumulatedContent = `${lastReceivedMessage.content ?? ""}${
  //           newMessage.content
  //         }`;
  //         if (lastReceivedMessage.id === newMessage.id) {
  //           if (newMessage.type === "chunk") {
  //             const updatedMessage = {
  //               ...lastReceivedMessage,
  //               content: accumulatedContent,
  //             };
  //             // clientLogger.debug("Accumulated message: ", accumulatedContent);
  //             return [...prevMsg.slice(0, -1), updatedMessage];
  //           } else {
  //             clientLogger.debug(
  //               lastMessage.id === newMessage.id,
  //               newMessage.type
  //             );
  //             return [...prevMsg];
  //           }
  //         } else {
  //           return [...prevMsg, newMessage];
  //         }
  //       case "error":
  //         clientLogger.error("Error parsing message: ", newMessage);
  //         return [...prevMsg];
  //       case "heartbeat":
  //         clientLogger.debug("Heartbeat received");
  //         return [...prevMsg];
  //       default:
  //         clientLogger.debug("Base case, no switch type match");
  //         clientLogger.debug("newMessage: ", newMessage);
  //         return [...prevMsg, newMessage];
  //     }
  //   });
  // }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue);
      dispatch({
        type: "ADD_MESSAGE",
        payload: {
          id: Date.now(),
          content: inputValue,
          type: "complete",
          sender: "user",
        } as WebSocketMessage,
      });
    }
    setInputValue("");
  }

  return (
    <div className="flex flex-col h-full w-full" ref={containerRef}>
      <ChatInterfaceHeader />
      <div className="flex-grow overflow-auto p-4">
        {msgList.map((message) => (
          <div
            key={message.id}
            className={`mb-4 whitespace-pre-wrap 
              ${message.sender === "user" ? "text-right" : "text-left"}
            `}
          >
            <span
              className={`inline-block p-2 rounded-lg ${
                message.sender === "user"
                  ? "bg-gray-50 text-gray-800 border border-gray-200"
                  : "bg-gray-200 text-black"
              }`}
            >
              {message.content}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <UserInputInterface
        inputValue={inputValue}
        onInputChange={setInputValue}
        onKeyDown={handleKeyDown}
        onSubmit={handleSubmit}
        maxHeight={maxTextareaHeight}
        ref={textareaRef}
      />
    </div>
  );
};

export default ChatInterface;
