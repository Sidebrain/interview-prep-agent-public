import { z } from "zod";

export type WebSocketHookOptions = {
  url: string;
  protocols?: string | string[];
  reconnectInterval?: number;
  reconnectAttempts?: number;
  heartbeatInterval?: number;
};

export type MessageReduceAction =
  | { type: "ADD_CHUNK"; payload: WebSocketMessage }
  | { type: "COMPLETE"; payload: WebSocketMessage }
  | { type: "ADD_MESSAGE"; payload: WebSocketMessage };

export type WebSocketHookResult = {
  sendMessage: (
    data: string | ArrayBufferLike | Blob | ArrayBufferView
  ) => void;
  readyState: number;
  connectionStatus: string;
  msgList: WebSocketMessage[];
  dispatch: React.Dispatch<MessageReduceAction>;
};

export const WebsocketMessageZodType = z.object({
  id: z.number(),
  type: z.enum(["chunk", "complete", "error", "heartbeat", "structured"]),
  content: z.string().nullable(),
  sender: z.enum(["user", "bot"]),
  index: z.number().default(0),
});

export type WebSocketMessage = z.infer<typeof WebsocketMessageZodType>;

export type RoutingKeyType = "streaming" | "structured";

export type WebSocketSendType = {
  routing_key: RoutingKeyType;
  content: string;
};
