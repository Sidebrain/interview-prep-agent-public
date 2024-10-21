"use client";
import React, { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown, { Components, ExtraProps } from "react-markdown";
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import remarkGfm from "remark-gfm";

import useWebSocket from "@/hooks/useWebsocket";
import UserInputInterface from "./UserInputInterface";
import { RoutingKeyType, WebSocketMessage } from "@/types/websocketTypes";
import clientLogger from "@/app/lib/clientLogger";
import useVoice from "@/hooks/useVoice";
import { set } from "lodash";

interface CodeProps {
  node?: any;
  inline?: any;
  className?: any;
  children?: any;
}

const ChatInterfaceHeader = () => {
  return (
    <header className="border border-gray-200 bg-slate-100 rounded-sm items-center justify-center flex text-gray-800 p-4 h-8 ">
      <h1 className="text-md text-center">Header</h1>
    </header>
  );
};

const ChatInterface = () => {
  const [inputValue, setInputValue] = useState("");
  const { sendMessage, msgList, dispatch } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL as string,
  });
  const {
    getPermissionsAndStartRecording,
    stopRecording,
    isRecording,
    playRecording,
    stopPlaying,
    error,
    transcribeAudioChunk,
    audioChunks,
  } = useVoice({
    onTranscription: (result) => {
      setInputValue((prev) => prev + " " + result);
    },
  });
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

  function handleStructuredKeyDown(
    e: React.KeyboardEvent<HTMLTextAreaElement>,
    routingKey: RoutingKeyType
  ) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleStructuredSubmit(e, routingKey);
    }
  }

  async function handleStructuredSubmit(
    e: React.FormEvent,
    routingKey: RoutingKeyType
  ) {
    //
    e.preventDefault();
    if (inputValue.trim()) {
      const messageToSend = {
        routing_key: routingKey,
        content: inputValue,
      };
      sendMessage(
        JSON.stringify({
          routing_key: routingKey,
          content: inputValue,
        })
      );
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
  const components: Components = {
    code({ node, inline, className, children, ...props }: CodeProps) {
      const match = /language-(\w+)/.exec(className || "");
      clientLogger.debug("match: ", match, match?.[1]);
      return !inline && match ? (
        <div className="code-block-wrapper">
          <SyntaxHighlighter
            {...props}
            style={oneDark as { [key: string]: React.CSSProperties }}
            language={match[1]}
            PreTag="div"
            {...props}
            wrapLongLines={true}
            customStyle={{
              margin: 0,
              padding: "1rem",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
            codeTagProps={{
              style: { whiteSpace: "pre-wrap", wordBreak: "break-word" },
            }}
          >
            {String(children).replace(/\n$/, "")}
          </SyntaxHighlighter>
        </div>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    p({ children }) {
      return <p className="mb-2 last:mb-0">{children}</p>;
    },
  };

  const renderMessage = (message: WebSocketMessage) => (
    <div
      key={message.id}
      className={`mb-4 ${
        message.sender === "user" ? "text-right" : "text-left"
      }`}
    >
      <span
        className={`inline-block p-2 rounded-lg max-w-full ${
          message.sender === "user"
            ? "bg-gray-50 text-gray-800 border border-gray-200"
            : "bg-gray-200 text-black"
        }`}
      >
        <ReactMarkdown
          components={components}
          remarkPlugins={[remarkGfm]}
          className="markdown-content break-words"
        >
          {message.content?.trim()}
        </ReactMarkdown>
      </span>
    </div>
  );

  return (
    <div className="flex flex-col h-full w-full" ref={containerRef}>
      <ChatInterfaceHeader />
      <div className="flex-grow overflow-auto no-scrollbar p-4">
        {msgList.map(renderMessage)}
        <div ref={messagesEndRef} />
      </div>
      <UserInputInterface
        inputValue={inputValue}
        onStructuredSubmit={handleStructuredSubmit}
        onInputChange={setInputValue}
        onKeyDown={handleKeyDown}
        onStructuredKeyDown={handleStructuredKeyDown}
        onSubmit={handleSubmit}
        maxHeight={maxTextareaHeight}
        ref={textareaRef}
        stopRecording={stopRecording}
        getPermissionsAndStartRecording={getPermissionsAndStartRecording}
        isRecording={isRecording}
        playRecording={playRecording}
        stopPlaying={stopPlaying}
        transcribeAudioChunk={transcribeAudioChunk}
        audioChunks={audioChunks}
      />
    </div>
  );
};

export default ChatInterface;
