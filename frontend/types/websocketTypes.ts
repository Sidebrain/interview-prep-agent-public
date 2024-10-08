import { z } from "zod";

export type WebSocketHookOptions = {
  url: string;
  protocols?: string | string[];
  reconnectInterval?: number;
  reconnectAttempts?: number;
  heartbeatInterval?: number;
};

export type WebSocketHookResult = {
  sendMessage: (
    data: string | ArrayBufferLike | Blob | ArrayBufferView
  ) => void;
  lastMessage: WebSocketEventMap["message"] | null;
  readyState: number;
  connectionStatus: string;
};

const WebsocketMessageZodType = z.object({
  id: z.number(),
  text: z.string(),
  sender: z.union([z.literal("user"), z.literal("bot")]),
});

export type WebSocketMessage = z.infer<typeof WebsocketMessageZodType>;
