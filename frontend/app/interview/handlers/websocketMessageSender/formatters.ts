import { MessageFormatter, SendableMessage } from "./types";
import clientLogger from "@/app/lib/clientLogger";
import { WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";

// Formatter for user input messages
class UserInputMessageFormatter implements MessageFormatter<SendableMessage> {
  canFormat(data: unknown): data is SendableMessage {
    const canFormat = WebsocketFrameSchema.safeParse(data).success;
    clientLogger.debug("UserInputMessageFormatter format check", {
      data,
      canFormat,
    });
    return canFormat;
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
    const canFormat = typeof data === "string" && data === "ping";
    clientLogger.debug("PingMessageFormatter format check", {
      data,
      canFormat,
    });
    return canFormat;
  }

  format(data: string): string {
    clientLogger.debug("PingMessageFormatter format", {
      data,
    });
    return data;
  }
}

export { UserInputMessageFormatter, PingMessageFormatter };
