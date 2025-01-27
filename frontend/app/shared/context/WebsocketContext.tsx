"use client";
import React, { createContext, useContext, useEffect, useRef } from "react";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import { useWebSocket } from "../hooks/useWebSocket";

const WebsocketContext = createContext<ReturnType<typeof useWebSocket> | null>(
  null
);

export const WebsocketProvider: React.FC<{
  children: React.ReactNode;
  options: WebSocketHookOptions;
}> = ({ children, options }) => {
  // Use ref to maintain stable options reference
  const optionsRef = useRef(options);
  
  // Update ref if options change
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  // Use stable options reference
  const websocket = useWebSocket(optionsRef.current);

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