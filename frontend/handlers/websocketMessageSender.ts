import { WebsocketSendTypesSchema } from "@/types/WebsocketSendTypes";
import { create } from "lodash";
import { z } from "zod";

// Base interface for all the message formatters
interface MessageFormatter<T> {
  canFormat(data: unknown): data is T;
  format(data: T): string;
}

// Interface for the main message sender
interface MessageSender {
  send(data: unknown): boolean;
}

// Types of sendable types of message
type SendableMessage = z.infer<typeof WebsocketSendTypesSchema>;

// Formatter for user input messages
class UserInputMessageFormatter implements MessageFormatter<SendableMessage> {
  canFormat(data: unknown): data is SendableMessage {
    return WebsocketSendTypesSchema.safeParse(data).success;
  }

  format(data: SendableMessage): string {
    try {
      return JSON.stringify(data);
    } catch (error) {
      console.error("Error in UserInputMessageFormatter:", error);
      throw error;
    }
  }
}

export class WebsocketMessageSender implements MessageSender {
  private ws: WebSocket;
  private formatters: MessageFormatter<any>[];

  constructor(ws: WebSocket) {
    this.ws = ws;
    this.formatters = [new UserInputMessageFormatter()];
  }

  send(data: unknown): boolean {
    for (const formatter of this.formatters) {
      if (formatter.canFormat(data)) {
        const message = formatter.format(data as any);
        this.ws.send(message);
        return true;
      }
    }

    console.error("No formatter found for data: ", data);
    return false;
  }
}

export const createWebsocketMessageSender = (
  ws: WebSocket
): WebsocketMessageSender => {
  return new WebsocketMessageSender(ws);
};
