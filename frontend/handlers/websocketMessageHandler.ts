import { Action } from "@/reducers/messageFrameReducer";
import {
  WebsocketFrame,
  WebsocketFrameSchema,
} from "@/types/ScalableWebsocketTypes";
import { z } from "zod";

interface FrameHandler {
  handleFrame(frame: WebsocketFrame): void;
}

// Base strategy class for handling websocket frames
interface FrameStrategy {
  canHandle(frame: WebsocketFrame): boolean;
  handleFrame(frame: WebsocketFrame): Action;
}

// schema for parsing completion/content frames
const CompletionContentSchema = WebsocketFrameSchema.extend({
  type: z.literal("completion"),
  address: z.enum(["content", "thought", "artifact"]),
});

class CompletionContentStrategy implements FrameStrategy {
  canHandle(frame: WebsocketFrame): boolean {
    try {
      return CompletionContentSchema.safeParse(frame).success;
    } catch (error) {
      return false;
    }
  }
  handleFrame(frame: WebsocketFrame): Action {
    try {
      if (frame.address === "content") {
        return {
          type: "completion/content",
          payload: frame,
        };
      } else if (frame.address === "thought") {
        return {
          type: "completion/thought",
          payload: frame,
        };
      } else {
        return {
          type: "completion/artifact",
          payload: frame,
        };
      }
    } catch (error) {
      console.error("Error in CompletionContentStrategy:", error);
      throw error;
    }
  }
}

const InputContentSchema = WebsocketFrameSchema.extend({
  type: z.literal("input"),
  address: z.literal("human"),
});

class InputContentStrategy implements FrameStrategy {
  canHandle(frame: WebsocketFrame): boolean {
    try {
      return InputContentSchema.safeParse(frame).success;
    } catch (error) {
      return false;
    }
  }
  handleFrame(frame: WebsocketFrame): Action {
    console.log("InputContentStrategy handleFrame");
    try {
      return {
        type: "completion/content",
        payload: frame,
      };
    } catch (error) {
      console.error("Error in InputContentStrategy:", error);
      throw error;
    }
  }
}

export class WebsocketFrameHandler implements FrameHandler {
  private strategies: FrameStrategy[];
  private dispatch: React.Dispatch<Action>;

  constructor(dispatch: React.Dispatch<Action>) {
    this.dispatch = dispatch;
    this.strategies = [
      new CompletionContentStrategy(),
      new InputContentStrategy(),
    ];
  }

  handleFrame(frame: WebsocketFrame): void {
    console.log("frame received: ", frame);
    if (!frame) return;

    for (const strategy of this.strategies) {
      if (strategy.canHandle(frame)) {
        const action = strategy.handleFrame(frame);
        if (action) this.dispatch(action);
        return; // stop processing after first successful strategy
      }
    }
    console.log("No handler found for frame: ", frame);
  }
}

export const createWebsocketFrameHandler = (
  dispatch: React.Dispatch<Action>
): FrameHandler => {
  return new WebsocketFrameHandler(dispatch);
};
