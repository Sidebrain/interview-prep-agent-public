import clientLogger from "@/app/lib/clientLogger";
import { IncomingMessageProcessor } from "./types";

import { IncomingMessageHandler } from "./types";

export class BaseIncomingMessageHandler implements IncomingMessageHandler {
  private processors: IncomingMessageProcessor[] = [];

  addProcessor(processor: IncomingMessageProcessor): void {
    this.processors.push(processor);
  }

  handleIncomingMessage(message: unknown): void {
    // implement handling logic here
    try {
      if (message === "pong") return;
    } catch (error) {
      clientLogger.error("Failed to handle incoming message", {
        error,
      });
    }
  }
}

class PongProcessor implements IncomingMessageProcessor {
  canProcess(message: unknown): boolean {
    return message === "pong";
  }
  process(message: unknown): void {
    clientLogger.debug("Received pong message", {
      message,
    });
  }
}
