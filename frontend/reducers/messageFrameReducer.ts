import {
  CompletionFrameChunk,
  WebsocketFrame,
} from "@/types/ScalableWebsocketTypes";

export type FrameType = {
  frameId: string;
  contentFrame: CompletionFrameChunk;
  artefactFrames: CompletionFrameChunk[];
};

type ActionType =
  | "heartbeat"
  | "completion/content"
  | "streaming/content"
  | "streaming/artefact"
  | "completion/artefact";

export type Action = {
  type: ActionType;
  payload: WebsocketFrame;
};

const messageFrameReducer = (
  frameList: FrameType[] = [],
  action: Action
): FrameType[] => {
  console.log("messageFrameReducer entered");
  console.log("action: ", action);
  console.log("frameList: ", frameList);
  const { frameId, frame: incomingFrame, address, type } = action.payload;
  switch (action.type) {
    case "heartbeat": {
      // do nothing, return as is. heartbeat doesn't mutate state
      return frameList;
    }
    case "completion/content": {
      console.log("completion/content action entered");
      // ensure the address is completion
      if (address !== "content") {
        console.log("Invalid address for completion/content", address);
        return frameList;
      }
      // find appropriate frame index if it exists
      const frameIndexToUpdate = frameList.findIndex(
        (existingFrame) => existingFrame.frameId === frameId
      );

      // if frame not found, create a new frame
      if (frameIndexToUpdate === -1) {
        console.log("Frame not found, creating new frame");
        console.log("incomingFrame: ", incomingFrame);
        console.log("New Framelist");
        console.log(frameList);
        return [
          ...frameList,
          {
            frameId,
            contentFrame: incomingFrame,
            artefactFrames: [],
          } as FrameType,
        ];
      }
      const updatedFrame = {
        ...frameList[frameIndexToUpdate],
        contentFrame: incomingFrame,
      } as FrameType;

      const newFrameList = [
        ...frameList.slice(0, frameIndexToUpdate),
        updatedFrame,
        ...frameList.slice(frameIndexToUpdate + 1),
      ];

      return newFrameList;
    }
    default:
      return frameList;
  }
};

export default messageFrameReducer;
