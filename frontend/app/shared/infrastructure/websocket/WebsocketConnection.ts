import clientLogger from "@/app/lib/clientLogger";
import {
  createWebsocketMessageSender,
  WebsocketMessageSender,
} from "@/app/shared/handlers/websocketMessageSender/sender";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import EventEmitter from "events";
import { HeartbeatHandler } from "./handlers/HeartbeatHandler";
import { ReconnectHandler } from "./handlers/ReconnectionHandler";
import { WebsocketEventHandler } from "./handlers/EventHandler";
import { CustomWebSocketEventMap } from "./types";

class WebSocketConnection {
  private websocket: WebSocket | null = null;
  private eventEmitter: EventEmitter;
  private heartbeatHandler: HeartbeatHandler | null = null;
  private messageSender: WebsocketMessageSender | null = null;
  private reconnectHandler: ReconnectHandler | null = null;
  private eventHandler: WebsocketEventHandler | null = null;

  constructor(private readonly config: WebSocketHookOptions) {
    this.eventEmitter = new EventEmitter();
    this.initializeHandlers();
  }

  private initializeHandlers(): void {
    this.reconnectHandler = new ReconnectHandler(
      this.config.reconnectAttempts ?? 5,
      this.config.reconnectInterval ?? 3000,
      this.connect.bind(this)
    );
    this.heartbeatHandler = new HeartbeatHandler(
      this.config.heartbeatInterval ?? 30000,
      this.sendRawMessage.bind(this)
    );
  }

  getWebsocket(): WebSocket | null {
    return this.websocket;
  }

  connect(): void {
    clientLogger.debug("Attempting WebSocket connection", {
      url: this.config.url,
      protocols: this.config.protocols,
      existingSocket: !!this.websocket,
    });

    if (this.websocket) {
      this.cleanup();
    }

    this.websocket = new WebSocket(this.config.url, this.config.protocols);
    this.eventHandler = new WebsocketEventHandler(
      this.eventEmitter,
      this.websocket
    );
    this.eventHandler.setupEventListeners({
      onOpen: () => {
        this.reconnectHandler?.reset();
        this.heartbeatHandler?.start();
        this.messageSender = createWebsocketMessageSender(this.websocket!);
      },
      onClose: () => {
        this.heartbeatHandler?.stop();
        this.reconnectHandler?.handleReconnect();
      },
      onError: (error) => {
        this.eventEmitter.emit("error", error);
      },
    });
  }

  cleanup(): void {
    this.heartbeatHandler?.stop();
    this.eventHandler?.cleanup();
    this.eventEmitter.removeAllListeners();

    if (this.websocket) {
      this.websocket.close(1000, "Closing connection via cleanup");
      this.websocket = null;
      this.messageSender = null;
    }
  }

  sendMessage(data: unknown): void {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      clientLogger.error("Failed to send message - WebSocket not connected", {
        readyState: this.websocket?.readyState,
        data: JSON.stringify(data, null, 2),
        connectionStatus: this.getConnectionStatus(),
      });
      throw new Error("WebSocket is not connected");
    }

    if (!this.messageSender) {
      throw new Error("Message sender not initialized");
    }

    try {
      const success = this.messageSender.send(data);
      if (!success) {
        throw new Error("Failed to send message");
      }
      clientLogger.debug("Successfully sent WebSocket message", {
        timestamp: new Date().toISOString(),
      });

      // Optional: emit sent event
      this.eventEmitter.emit("messageSent", data);
    } catch (error) {
      clientLogger.error("Failed to send WebSocket message", {
        error: error instanceof Error ? error.message : String(error),
        data: JSON.stringify(data, null, 2),
        stack: error instanceof Error ? error.stack : undefined,
      });
      throw error;
    }
  }
  private sendRawMessage(data: string): void {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      clientLogger.debug("Cannot send heartbeat - connection not open");
      return;
    }
    this.websocket.send(data);
  }

  getConnectionStatus(): string {
    if (!this.websocket) return "No WebSocket Instance";

    switch (this.websocket.readyState) {
      case WebSocket.CONNECTING:
        return "CONNECTING";
      case WebSocket.OPEN:
        return "OPEN";
      case WebSocket.CLOSING:
        return "CLOSING";
      case WebSocket.CLOSED:
        return "CLOSED";
      default:
        return "UNKNOWN";
    }
  }

  on<K extends keyof CustomWebSocketEventMap>(
    event: K,
    listener: (event: CustomWebSocketEventMap[K]) => void
  ): void {
    this.eventEmitter.on(event, listener);
  }

  off<K extends keyof CustomWebSocketEventMap>(
    event: K,
    listener: (event: CustomWebSocketEventMap[K]) => void
  ): void {
    this.eventEmitter.off(event, listener);
  }

  getReadyState(): number {
    return this.websocket?.readyState ?? WebSocket.CLOSED;
  }
}

export default WebSocketConnection;
