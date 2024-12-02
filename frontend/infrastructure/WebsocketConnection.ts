import clientLogger from "@/app/lib/clientLogger";
import { WebsocketMessageSender } from "@/handlers/websocketMessageSender";
import { WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";
import { WebSocketHookOptions } from "@/types/websocketTypes";
import EventEmitter from "events";

export type CustomWebSocketEventMap = WebSocketEventMap & {
  heartbeat: void;
};

class WebSocketConnection {
  private websocket: WebSocket | null = null;
  private config: WebSocketHookOptions;
  private eventEmitter: EventEmitter;
  private reconnectCount: number = 0;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageSender: WebsocketMessageSender | null = null;

  constructor(config: WebSocketHookOptions) {
    this.config = config;
    this.eventEmitter = new EventEmitter();
    this.cleanupAllListeners();
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
      this.cleanupAllListeners();
      this.disconnect();
    }

    this.websocket = new WebSocket(this.config.url, this.config.protocols);
    this.setupEventListeners();
  }

  private cleanupEventListeners(): void {
    if (this.websocket) {
      this.websocket.onopen = null;
      this.websocket.onclose = null;
      this.websocket.onerror = null;
      this.websocket.onmessage = null;
    }
  }

  private cleanupAllListeners(): void {
    this.cleanupEventListeners();

    // remove all listeners from the event emitter
    this.eventEmitter.removeAllListeners("heartbeat");
    // this.eventEmitter.removeAllListeners("message");
  }

  private setupEventListeners(): void {
    if (!this.websocket) return;

    this.websocket.onopen = (event: CustomWebSocketEventMap["open"]) => {
      clientLogger.debug("WebSocket opened", {
        url: this.config.url,
        protocols: this.config.protocols,
        readyState: this.websocket?.readyState,
      });

      this.reconnectCount = 0;
      this.startHeartbeat();
      this.messageSender = new WebsocketMessageSender(this.websocket!);
      this.eventEmitter.emit("open", event);
    };

    this.websocket.onclose = (event: CustomWebSocketEventMap["close"]) => {
      clientLogger.debug("WebSocket closed", {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.websocket?.readyState,
      });

      this.stopHeartbeat();
      this.eventEmitter.emit("close", event);
      this.handleReconnect();
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
      //! TODO: you dont need to parse the data here
      const parsedData = JSON.parse(event.data);
      this.eventEmitter.emit("message", parsedData);
    } catch (error) {
      this.eventEmitter.emit(
        "error",
        new Error(`Failed to parse message ${error}`)
      );
    }
  }

  private handleReconnect(): void {
    // clean up before reconnecting
    // this.cleanupAllListeners();
    this.cleanupEventListeners();
    this.stopHeartbeat();

    if (this.reconnectCount < (this.config.reconnectAttempts ?? 5)) {
      setTimeout(() => {
        this.reconnectCount++;

        clientLogger.debug("Reconnecting to WebSocket", {
          reconnectCount: this.reconnectCount,
        });

        this.connect();
      }, this.config.reconnectInterval ?? 3000);
    }
  }

  // also clean this up
  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      this.sendMessage("ping");
    }, this.config.heartbeatInterval ?? 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
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

    try {
      if (this.messageSender) {
        const success = this.messageSender.send(data);
        if (!success) {
          throw new Error("Failed to send message");
        }
        //     const message = typeof data === "string" ? data : JSON.stringify(data);

        //   clientLogger.debug("Sending WebSocket message", {
        //     messageType: typeof data,
        //     message: JSON.stringify(data, null, 2),
        //     readyState: this.websocket.readyState,
        //     connectionStatus: this.getConnectionStatus(),
        //   });

        //   this.websocket.send(message);

        clientLogger.debug("Successfully sent WebSocket message", {
          timestamp: new Date().toISOString(),
        });

        // Optional: emit sent event
        this.eventEmitter.emit("messageSent", data);
      }
    } catch (error) {
      clientLogger.error("Failed to send WebSocket message", {
        error: error instanceof Error ? error.message : String(error),
        data: JSON.stringify(data, null, 2),
        stack: error instanceof Error ? error.stack : undefined,
      });
      throw error;
    }
  }

  sendHumanInput(content: string): void {
    if (!this.messageSender) {
      throw new Error("Message sender not initialized");
    }

    const frame = this.messageSender.createHumanInputFrame(content);
    this.sendMessage(frame);
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

  disconnect(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
      this.messageSender = null;
      this.cleanupAllListeners();
    }
    this.stopHeartbeat();
  }

  getReadyState(): number {
    return this.websocket?.readyState ?? WebSocket.CLOSED;
  }

  createHumanInputFrame(content: string): WebsocketFrame {
    return this.messageSender?.createHumanInputFrame(content) ?? {};
  }
}

export default WebSocketConnection;
