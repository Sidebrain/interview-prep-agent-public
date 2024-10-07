"use client";
import React, { useState, useRef, useEffect } from "react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import useWebSocket from "@/app/hooks/useWebsocket";
import clientLogger from "@/app/lib/clientLogger";

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

  clientLogger.debug("ws connection");
  clientLogger.debug(connectionStatus, readyState, sendMessage);

  // bring the last message into the view
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

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

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    adjustTextareaHeight();
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const newHeight = Math.min(
        textareaRef.current.scrollHeight,
        maxTextareaHeight
      );
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };
  ////////

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setMessages([
        ...messages,
        { id: messages.length + 1, text: inputValue, sender: "user" },
      ]);
      setInputValue("");
      adjustTextareaHeight();
    }
  };

  return (
    <div className="flex flex-col h-full w-full" ref={containerRef}>
      <header className="bg-gray-500 rounded-sm items-center justify-center flex text-white p-4 h-8 ">
        <h1 className="text-md text-center">Header</h1>
      </header>

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

      <div className="bg-white p-2">
        <form onSubmit={handleSubmit} className="flex">
          <Textarea
            ref={textareaRef}
            value={inputValue}
            onKeyDown={handleKeyDown}
            onChange={handleInputChange}
            placeholder="Type a message..."
            className="flex-grow p-2 border rounded-lg resize-none mr-2"
            style={{ maxHeight: `${maxTextareaHeight}px` }}
            rows={1}
          />
          <Button
            type="submit"
            className="self-end"
            // className="bg-blue-500 text-white px-4 py-2 rounded-lg"
          >
            Send
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
