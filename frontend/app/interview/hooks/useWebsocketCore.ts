"use client";
import clientLogger from "@/app/lib/clientLogger";
import { useCallback, useEffect, useReducer, useRef } from "react";
import { WebSocketCoreOptions } from "../types/websocketConnectionTypes";
import WebsocketConnection from "../infrastructure/websocket/WebsocketConnection";

export const useWebsocketCore = <TState, TAction, T>({
  reducer,
  initialState,
  validator: websocketMessageValidator,
  ...config
}: WebSocketCoreOptions<TState, TAction, T>) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const connectionRef = useRef<WebsocketConnection | null>(null);

  useEffect(() => {
    if (!config.enabled) return;

    if (!connectionRef.current) {
      connectionRef.current = new WebsocketConnection(config);
    }

    const connection = connectionRef.current;

    connection.on("message", (rawData: unknown) => {
      try {
        const validatedData = websocketMessageValidator.validate(rawData);
        clientLogger.debug("Received valid WebSocket message", {
          validatedData,
        });

        // dispatch here
        clientLogger.debug("Validated WebSocket message", {
          validatedData,
        });
        dispatch({
          type: "ADD_FRAME",
          payload: validatedData,
        } as TAction);
      } catch (error) {
        clientLogger.error("Failed to parse WebSocket message", {
          error,
        });
      }
    });

    connection.on("open", (event) => {
      clientLogger.debug("WebSocket connection opened", {
        event,
      });
    });

    connection.on("close", (event) => {
      clientLogger.debug("WebSocket connection closed", {
        event,
      });
    });

    connection.on("error", (error) => {
      clientLogger.error("WebSocket connection error", {
        error,
      });
    });

    connection.on("heartbeat", (event) => {
      clientLogger.debug("Received heartbeat from server", {
        event,
      });
    });

    connection.connect();

    return () => {
      // clean up here
      connection.cleanup();
    };
  }, [config.enabled, config.url]);

  const sendMessage = useCallback(
    (data: any) => {
      if (!connectionRef.current) {
        throw new Error("Websocket connection not initialized");
      }
      clientLogger.debug("Sending message to WebSocket", {
        data,
      });
      return connectionRef.current.sendMessage(data);
    },
    [connectionRef.current]
  );

  return {
    state,
    dispatch,
    connection: connectionRef.current,
    connectionStatus: connectionRef.current?.getConnectionStatus(),
    sendMessage,
  };
};
