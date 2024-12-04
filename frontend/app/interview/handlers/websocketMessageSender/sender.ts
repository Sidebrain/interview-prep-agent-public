import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import { v4 as uuidv4 } from "uuid";
import { createHumanInputFrame } from "@/app/lib/helperFunctions";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import clientLogger from "@/app/lib/clientLogger";
import {
  MessageFormatter,
  MessageSender,
} from "@/app/interview/handlers/websocketMessageSender/types";
import { PingMessageFormatter, UserInputMessageFormatter } from "./formatters";

export class WebsocketMessageSender implements MessageSender {
  private ws: WebSocket;
  private formatters: MessageFormatter<any>[];

  constructor(ws: WebSocket) {
    this.ws = ws;
    this.formatters = [
      new UserInputMessageFormatter(),
      new PingMessageFormatter(),
    ];
  }

  send(data: unknown): boolean {
    clientLogger.debug("WebsocketMessageSender send", {
      data,
    });
    for (const formatter of this.formatters) {
      if (formatter.canFormat(data)) {
        const message = formatter.format(data as unknown);
        this.ws.send(message);
        return true;
      }
    }

    clientLogger.error("No formatter found for data: ", {
      data,
    });
    return false;
  }

  createRegenerateSignalFrame(
    frameToRegenerate: CompletionFrameChunk
  ): WebsocketFrame {
    return {
      frameId: uuidv4(),
      correlationId: uuidv4(),
      type: "signal.regenerate",
      address: "human",
      frame: frameToRegenerate,
    };
  }
  createHumanInputFrame(content: string): WebsocketFrame {
    return createHumanInputFrame(content);
  }
}

export const createWebsocketMessageSender = (
  ws: WebSocket
): WebsocketMessageSender => {
  return new WebsocketMessageSender(ws);
};
