"use client";
import React, { useState, useRef, useEffect } from "react";
import useWebSocket from "@/app/hooks/useWebsocket";
import clientLogger from "@/app/lib/clientLogger";
import UserInputInterface from "./UserInputInterface";

const ChatInterfaceHeader = () => {
  return (
    <header className="border border-gray-200 bg-slate-100 rounded-sm items-center justify-center flex text-gray-800 p-4 h-8 ">
      <h1 className="text-md text-center">Header</h1>
    </header>
  );
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello!", sender: "user" },
    { id: 2, text: "Hi there!", sender: "bot" },
  ]);
  const { connectionStatus, readyState, sendMessage } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL as string,
  });
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [maxTextareaHeight, setMaxTextareaHeight] = useState<number>(150);

  clientLogger.debug(connectionStatus, readyState, sendMessage);

  // bring the last message into the view
  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(scrollToBottom, [messages]);

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (inputValue.trim()) {
      setMessages([
        ...messages,
        { id: messages.length + 1, text: inputValue, sender: "user" },
      ]);
      setInputValue("");
    }
  }

  return (
    <div className="flex flex-col h-full w-full" ref={containerRef}>
      <ChatInterfaceHeader />
      <div className="flex-grow overflow-auto p-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-4 whitespace-pre-wrap ${
              message.sender === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block p-2 rounded-lg ${
                message.sender === "user"
                  ? "bg-gray-50 text-gray-800 border border-gray-200"
                  : "bg-gray-200 text-black"
              }`}
            >
              {message.text}
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
