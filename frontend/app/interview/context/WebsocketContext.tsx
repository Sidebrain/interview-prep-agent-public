"use client";
import React, { createContext, useContext } from "react";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import { useWebSocket } from "@/app/interview/hooks/useWebSocket";

const WebsocketContext = createContext<ReturnType<typeof useWebSocket> | null>(
  null
);

export const WebsocketProvider: React.FC<{
  children: React.ReactNode;
  options: WebSocketHookOptions;
}> = ({ children, options }) => {
  const websocket = useWebSocket(options);

  return (
    <WebsocketContext.Provider value={websocket}>
      {children}
    </WebsocketContext.Provider>
  );
};

export const useWebsocketContext = () => {
  const context = useContext(WebsocketContext);
  if (!context) {
    throw new Error(
      "useWebsocketContext must be used within a WebsocketProvider"
    );
  }
  return context;
};