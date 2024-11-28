import { WebSocketMessage } from "./websocketTypes";

export enum WebSocketEvents {
  OPEN = "open",
  CLOSE = "close",
  MESSAGE = "message",
  ERROR = "error",
  HEARTBEAT = "heartbeat",
}

export interface WebSocketEventMap {
  [WebSocketEvents.OPEN]: void;
  [WebSocketEvents.CLOSE]: void;
  [WebSocketEvents.MESSAGE]: WebSocketMessage;
  [WebSocketEvents.ERROR]: Error;
  [WebSocketEvents.HEARTBEAT]: void;
}
