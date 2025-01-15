import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

type CustomWebSocketEventMap = WebSocketEventMap & {
  heartbeat: void;
};

interface IncomingMessageProcessor {
  canProcess(message: unknown): boolean;
  process(message: unknown): void;
}

interface IncomingMessageHandler {
  addProcessor(processor: IncomingMessageProcessor): void;
  handleIncomingMessage(message: unknown): void;
}

export type { IncomingMessageProcessor, IncomingMessageHandler, CustomWebSocketEventMap };
