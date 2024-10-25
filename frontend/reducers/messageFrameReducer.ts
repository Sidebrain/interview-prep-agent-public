import {
  CompletionFrameChunk,
  WebsocketFrame,
} from "@/types/ScalableWebsocketTypes";

type FrameType = {
  frameId: string;
  content: CompletionFrameChunk;
  artefacts: CompletionFrameChunk[];
};

type ActionType =
  | "heartbeat"
  | "completion/content"
  | "streaming/content"
  | "streaming/artefact"
  | "completion/artefact";

type Action = {
  type: ActionType;
  payload: WebsocketFrame;
};

const messageFrameReducer = (
  frameList: FrameType[] = [],
  action: Action
): FrameType[] => {
  const { frameId, frame: incomingFrame, address, type } = action.payload;
  switch (action.type) {
    case "heartbeat": {
      // do nothing, return as is. heartbeat doesn't mutate state
      return frameList;
    }
    case "completion/content": {
      // find appropriate frame index if it exists
      const frameIndexToUpdate = frameList.findIndex(
        (existingFrame) => existingFrame.frameId === frameId
      );

      // if frame not found, create a new frame
      if (frameIndexToUpdate === -1) {
        return [
          ...frameList,
          {
            frameId,
            content: incomingFrame,
            artefacts: [],
          } as FrameType,
        ];
      }
      const updatedFrame = {
        ...frameList[frameIndexToUpdate],
        content: incomingFrame,
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
