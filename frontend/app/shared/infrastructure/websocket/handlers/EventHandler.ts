import clientLogger from "@/app/lib/clientLogger";
import EventEmitter from "events";
import { CustomWebSocketEventMap } from "../types";

export class WebsocketEventHandler {
  constructor(
    private eventEmitter: EventEmitter,
    private websocket: WebSocket
  ) {}

  setupEventListeners(callbacks: {
    onOpen: () => void;
    onClose: () => void;
    onError: (error: Error) => void;
  }): void {
    if (!this.websocket) return;

    this.websocket.onopen = (event: CustomWebSocketEventMap["open"]) => {
      clientLogger.debug("WebSocket opened", {
        readyState: this.websocket?.readyState,
      });
      callbacks.onOpen();

      this.eventEmitter.emit("open", event);
    };

    this.websocket.onclose = (event: CustomWebSocketEventMap["close"]) => {
      clientLogger.debug("WebSocket closed", {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.websocket?.readyState,
      });
      callbacks.onClose();
      this.eventEmitter.emit("close", event);
    };

    this.websocket.onerror = (event: CustomWebSocketEventMap["error"]) => {
      clientLogger.error("WebSocket error", {
        error: event,
        readyState: this.websocket?.readyState,
      });

      this.eventEmitter.emit("error", event);
    };

    this.websocket.onmessage = (event: CustomWebSocketEventMap["message"]) => {
      this.handleMessage(event);
    };

  }

  private handleMessage(event: MessageEvent<string>): void {
    if (event.data === "pong") {
      this.eventEmitter.emit("heartbeat");
      return;
    }
    try {
      const parsedData = JSON.parse(event.data);
      this.eventEmitter.emit("message", parsedData);
    } catch (error) {
      this.eventEmitter.emit(
        "error",
        new Error(`Failed to parse message ${error}`)
      );
    }
  }

  cleanup(): void {
    if (this.websocket) {
      this.websocket.onopen = null;
      this.websocket.onclose = null;
      this.websocket.onerror = null;
      this.websocket.onmessage = null;
    }
  }
}
