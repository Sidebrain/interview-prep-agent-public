import { WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";
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
type SendableMessage = z.infer<typeof WebsocketFrameSchema>;

export type { MessageFormatter, MessageSender, SendableMessage };
