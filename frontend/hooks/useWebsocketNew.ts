"use client";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import { useEffect, useRef, useState, useCallback, useReducer } from "react";
import clientLogger from "../app/lib/clientLogger";
import {
  WebsocketFrame,
  WebsocketFrameSchema,
} from "@/types/ScalableWebsocketTypes";
import messageFrameReducer, {
  Action,
  FrameType,
} from "@/reducers/messageFrameReducer";
import { createWebsocketFrameHandler } from "@/handlers/websocketMessageHandler";
import {
  createWebsocketMessageSender,
  WebsocketMessageSender,
} from "@/handlers/websocketMessageSender";

type WebsocketHookResultNew = {
  sendMessage: (data: WebsocketFrame) => void;
  readyState: number;
  connectionStatus: string;
  frameList: FrameType[];
  dispatch: React.Dispatch<Action>;
  frameHandler: (frame: WebsocketFrame) => void;
};

const useWebSocket = ({
  url,
  enabled,
  protocols,
  reconnectInterval = 5000,
  reconnectAttempts = 5,
  heartbeatInterval = 10000,
}: WebSocketHookOptions): WebsocketHookResultNew => {
  const [frameList, dispatch] = useReducer(messageFrameReducer, []);
  const [readyState, setReadyState] = useState<number>(WebSocket.CLOSED);
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Disconnected");

  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef<number>(0);
  const heartbeatTimer = useRef<NodeJS.Timeout | null>(null);
  const websocketFrameHandlerRef = useRef(
    createWebsocketFrameHandler(dispatch)
  );
  const senderRef = useRef<WebsocketMessageSender | null>(null);

  const startHeartbeat = useCallback(() => {
    clientLogger.debug("Starting heartbeat");
    heartbeatTimer.current = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        clientLogger.debug("Sending heartbeat");
        ws.current.send("ping");
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
    }
  }, []);

  const connect = useCallback(() => {
    // websocket already exists
    clientLogger.debug("useWebSocket triggered");
    if (ws.current) {
      clientLogger.debug("Websocket already initialized");
      return;
    }

    // create new websocket connection
    ws.current = new WebSocket(url, protocols);
    setConnectionStatus("Connecting");
    clientLogger.debug("connecting to websocket at url: ", url);

    // what happens onopen
    ws.current.onopen = () => {
      clientLogger.debug("WebSocket connection established");
      setReadyState(WebSocket.OPEN);
      setConnectionStatus("Connected");
      reconnectCount.current = 0;
      startHeartbeat();
    };

    // what happens on close
    ws.current.onclose = (event) => {
      clientLogger.debug("WebSocket connection closed:", event);
      setReadyState(WebSocket.CLOSED);
      setConnectionStatus("Disconnected");
      stopHeartbeat();

      if (reconnectCount.current < reconnectAttempts) {
        setTimeout(() => {
          reconnectCount.current += 1;
          connect();
        }, reconnectInterval);
      } else {
        setConnectionStatus("Max reconnect attempts reached");
      }
    };

    // what happens on error
    ws.current.onerror = (error) => {
      clientLogger.error("WebSocket error:", error);
      setConnectionStatus("Error");
    };

    // what happens when message is received
    ws.current.onmessage = (event: WebSocketEventMap["message"]) => {
      // clientLogger.debug("WebSocket message received:", event.data);
      try {
        if (event.data === "pong") {
          // Heartbeat response received
          clientLogger.debug("Heartbeat response ** pong ** received");
          return;
        }

        console.log("message received: ", event.data);

        const data = JSON.parse(event.data);
        const websocketFrame = WebsocketFrameSchema.parse(data);

        // let the handler handle the frame
        frameHandler(websocketFrame);
      } catch (error) {
        clientLogger.error("Error parsing message: ", error);
        clientLogger.error("Message data: ", event.data);
      }
    };
  }, [
    url,
    protocols,
    reconnectInterval,
    reconnectAttempts,
    heartbeatInterval,
    startHeartbeat,
    stopHeartbeat,
  ]);

  const frameHandler = useCallback((frame: WebsocketFrame) => {
    websocketFrameHandlerRef.current.handleFrame(frame);
  }, []);

  const disconnect = useCallback(() => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.close(1000, "component unmounting");
      if (reconnectCount.current) {
        clearTimeout(reconnectCount.current);
      }
    } else {
      clientLogger.debug("No websocket connection to close.");
    }
  }, []);

  const sendMessage = useCallback(
    // (data: string | ArrayBufferLike | Blob | ArrayBufferView) => {
    (data: WebsocketFrame) => {
      clientLogger.debug("Attempting to send message: ", data);
      // if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      //   ws.current.send(data);
      if (!senderRef.current) {
        clientLogger.error("No sender found");
        return false;
      } else {
        // clientLogger.error("WebSocket is not connected");
        return senderRef.current.send(data);
      }
    },
    []
  );

  useEffect(() => {
    // connect to websocket
    if (!enabled) {
      clientLogger.debug("url not ready, waiting for url to be loaded");
      return;
    }
    connect();

    return () => {
      clientLogger.debug("useWebSocket cleanup triggered, disconnecting");
      disconnect();
      stopHeartbeat();
    };
  }, [connect, disconnect, stopHeartbeat, enabled]);

  useEffect(() => {
    // create message sender
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      senderRef.current = createWebsocketMessageSender(ws.current);
      clientLogger.debug("webcocket message sender created");
    }
    return () => {
      senderRef.current = null;
    };
  }, [ws.current?.readyState]);

  return {
    sendMessage,
    frameList,
    readyState,
    connectionStatus,
    dispatch,
    frameHandler,
  };
};

export default useWebSocket;
