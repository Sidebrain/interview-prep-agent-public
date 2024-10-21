"use client";
import {
  WebSocketHookOptions,
  WebSocketHookResult,
  WebSocketMessage,
  WebsocketMessageZodType,
} from "@/types/websocketTypes";
import { useEffect, useRef, useState, useCallback, useReducer } from "react";
import clientLogger from "../app/lib/clientLogger";
import messageReducer from "../reducers/messageReducer";

const useWebSocket = ({
  url,
  protocols,
  reconnectInterval = 5000,
  reconnectAttempts = 5,
  heartbeatInterval = 30000,
}: WebSocketHookOptions): WebSocketHookResult => {
  const [msgList, dispatch] = useReducer(messageReducer, [
    { id: 1, content: "Hello!", type: "complete", sender: "bot", index: 0 },
    { id: 2, content: "Hi there!", type: "complete", sender: "user", index: 0 },
  ]);
  const [readyState, setReadyState] = useState<number>(WebSocket.CLOSED);
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Disconnected");

  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef<number>(0);
  const heartbeatTimer = useRef<NodeJS.Timeout | null>(null);

  const startHeartbeat = useCallback(() => {
    heartbeatTimer.current = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
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
        const data = JSON.parse(event.data);
        const message = WebsocketMessageZodType.parse(data);
        // clientLogger.debug("Parsed message: ", message);

        if (message.type === "heartbeat") {
          // Heartbeat response received
          clientLogger.debug("Heartbeat response received");
          return;
        }
        // clientLogger.debug("Setting last message: ", message);
        if (message.type === "chunk") {
          dispatch({ type: "ADD_CHUNK", payload: message });
        } else if (message.type === "complete") {
          dispatch({ type: "COMPLETE", payload: message });
        }
        if (message.type === "structured") {
          // clientLogger.debug("Structured message received: ", message);
          dispatch({ type: "ADD_MESSAGE", payload: message });
        }
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
    (data: string | ArrayBufferLike | Blob | ArrayBufferView) => {
      clientLogger.debug("Attempting to send message: ", data);
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(data);
      } else {
        clientLogger.error("WebSocket is not connected");
      }
    },
    []
  );

  useEffect(() => {
    connect();

    return () => {
      clientLogger.debug("useWebSocket cleanup triggered, disconnecting");
      disconnect();
      stopHeartbeat();
    };
  }, [connect, disconnect, stopHeartbeat]);

  return { sendMessage, msgList, readyState, connectionStatus, dispatch };
};

export default useWebSocket;
