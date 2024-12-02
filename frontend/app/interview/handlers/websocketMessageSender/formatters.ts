import { MessageFormatter, SendableMessage } from "./types";
import clientLogger from "@/app/lib/clientLogger";
import { WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";

// Formatter for user input messages
class UserInputMessageFormatter implements MessageFormatter<SendableMessage> {
  canFormat(data: unknown): data is SendableMessage {
    return WebsocketFrameSchema.safeParse(data).success;
  }

  format(data: SendableMessage): string {
    clientLogger.debug("UserInputMessageFormatter format", {
      data,
    });
    try {
      return JSON.stringify(data);
    } catch (error) {
      console.error("Error in UserInputMessageFormatter:", error);
      throw error;
    }
  }
}

// Formatter for ping messages
class PingMessageFormatter implements MessageFormatter<string> {
  canFormat(data: unknown): data is string {
    return typeof data === "string" && data === "ping";
  }

  format(data: string): string {
    clientLogger.debug("PingMessageFormatter format", {
      data,
    });
    return data;
  }
}

export { UserInputMessageFormatter, PingMessageFormatter };
