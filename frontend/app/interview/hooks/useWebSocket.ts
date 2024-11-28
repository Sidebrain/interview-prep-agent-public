"use client";
import { WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";
import { ZodMessageValidator } from "../websocketMessageValidator";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import { useWebsocketCore } from "./useWebsocketCore";
import { frameReducer, initialFrameState } from "../reducers/frameReducer";
import { useMemo } from "react";

export const useWebSocket = (config: WebSocketHookOptions) => {
  const validator = useMemo(
    () => new ZodMessageValidator(WebsocketFrameSchema),
    []
  );
  return useWebsocketCore({
    ...config,
    validator,
    reducer: frameReducer,
    initialState: initialFrameState,
  });
};
