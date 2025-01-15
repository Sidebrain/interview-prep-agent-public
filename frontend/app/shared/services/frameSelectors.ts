import type {
  WebsocketFrame,
  AddressType,
} from "@/types/ScalableWebsocketTypes";

// AddressType is a union type of strings:
// "content" | "artifact" | "human" | "thought" | "evaluation"
// (typeof AddressType)[number][] creates an array type of those string literals
type ConversationAddressTypes = (typeof AddressType)[number][];

export const frameSelectors = {
  conversation: (websocketFrames: WebsocketFrame[]) => {
    const selectTypes: ConversationAddressTypes = [
      "content",
      "human",
      "thought",
    ];

    return websocketFrames.filter((websocketFrame) =>
      selectTypes.includes(
        websocketFrame.address as (typeof AddressType)[number]
      )
    );
  },

  perspective: (websocketFrames: WebsocketFrame[]) => {
    const selectTypes: ConversationAddressTypes = ["perspective"];
    return websocketFrames.filter((websocketFrame) =>
      selectTypes.includes(
        websocketFrame.address as (typeof AddressType)[number]
      )
    );
  },

  evaluation: (websocketFrames: WebsocketFrame[]) => {
    const selectTypes: ConversationAddressTypes = ["evaluation"];
    return websocketFrames.filter((websocketFrame) =>
      selectTypes.includes(
        websocketFrame.address as (typeof AddressType)[number]
      )
    );
  },

  thought: (websocketFrames: WebsocketFrame[]) => {
    const selectTypes: ConversationAddressTypes = ["thought"];
    return websocketFrames.filter((websocketFrame) =>
      selectTypes.includes(
        websocketFrame.address as (typeof AddressType)[number]
      )
    );
  },

  lastThought: (websocketFrames: WebsocketFrame[]) => {
    if (!websocketFrames || websocketFrames.length === 0) {
      return [];
    }
    const thoughtFrames = frameSelectors.thought(websocketFrames);
    if (thoughtFrames.length === 0) {
      return [];
    }
    return [thoughtFrames[thoughtFrames.length - 1]];
  },
};
