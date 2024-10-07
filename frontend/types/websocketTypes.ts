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
