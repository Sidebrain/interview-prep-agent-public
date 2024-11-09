import { CompletionFrameChunk, WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";
import { z } from "zod";
import { v4 as uuidv4 } from "uuid";
import { createTimestamp } from "@/app/lib/helperFunctions";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { FrameType } from "@/types/reducerTypes";

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
type SendableMessage = z.infer<typeof WebsocketFrameSchema>;

// Formatter for user input messages
class UserInputMessageFormatter implements MessageFormatter<SendableMessage> {
  canFormat(data: unknown): data is SendableMessage {
    return WebsocketFrameSchema.safeParse(data).success;
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
    console.log("Sending data: ", data);
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

  createRegenerateSignalFrame(
    frameToRegenerate: CompletionFrameChunk
  ): WebsocketFrame {
    return {
      frameId: uuidv4(),
      type: "signal.regenerate",
      address: "human",
      frame: frameToRegenerate,
    };
  }

  createHumanInputFrame(content: string): WebsocketFrame {
    return {
      frameId: uuidv4(),
      type: "input",
      address: "human",
      frame: {
        id: uuidv4(),
        object: "human.completion",
        model: "infinity",
        role: "user",
        content: content,
        createdTs: createTimestamp(),
        title: null,
        delta: null,
        index: 0,
        finishReason: "stop",
      },
    };
  }
}

export const createWebsocketMessageSender = (
  ws: WebSocket
): WebsocketMessageSender => {
  return new WebsocketMessageSender(ws);
};
