import { v4 as uuidv4 } from "uuid";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

const createTimestamp = () => {
  return Math.floor(Date.now() / 1000);
};

export { createTimestamp };

export const createHumanInputFrame = (content: string): WebsocketFrame => {
  return {
    frameId: uuidv4(),
    correlationId: uuidv4(),
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
};
