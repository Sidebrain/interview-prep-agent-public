import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import { FrameType, Action } from "@/types/reducerTypes";

const messageFrameReducer = (
  frameList: FrameType[] = [],
  action: Action
): FrameType[] => {
  console.log("messageFrameReducer entered");
  console.log("action: ", action);
  console.log("frameList: ", frameList);
  const { frameId, frame: incomingFrame, address } = action.payload;
  switch (action.type) {
    case "heartbeat": {
      // do nothing, return as is. heartbeat doesn't mutate state
      return frameList;
    }

    case "completion/content": {
      console.log("completion/content action entered");
      // ensure the address is completion
      if (address !== "content" && address !== "human") {
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
        return [
          ...frameList,
          {
            frameId,
            contentFrame: incomingFrame,
            artifactFrames: [],
            thoughtFrames: [],
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

    case "completion/thought": {
      //
      console.log("completion/thought action entered");
      // ensure the address is completion
      if (address !== "thought") {
        console.log("Invalid address for completion/thought", address);
        return frameList;
      }

      // find appropriate frame index if it exists
      const frameIndexToUpdate = frameList.findIndex(
        (existingFrame) => existingFrame.frameId === frameId
      );

      // if frame not found, create a new frame
      if (frameIndexToUpdate === -1) {
        console.log("Frame not found, creating new frame");
        return [
          ...frameList,
          {
            frameId,
            contentFrame: {} as CompletionFrameChunk,
            artifactFrames: [],
            thoughtFrames: [incomingFrame],
          } as FrameType,
        ];
      }

      const updatedFrame = {
        ...frameList[frameIndexToUpdate],
        thoughtFrames: [
          ...frameList[frameIndexToUpdate].thoughtFrames,
          incomingFrame,
        ],
      } as FrameType;

      const newFrameList = [
        ...frameList.slice(0, frameIndexToUpdate),
        updatedFrame,
        ...frameList.slice(frameIndexToUpdate + 1),
      ];

      return newFrameList;
    }

    case "completion/artifact": {
      console.log("completion/artifact action entered");
      // ensure the address is artifact
      if (address !== "artifact") {
        console.log("Invalid address for completion/artifact", address);
        return frameList;
      }

      // find appropriate frame index if it exists
      const frameIndexToUpdate = frameList.findIndex(
        (existingFrame) => existingFrame.frameId === frameId
      );

      // if frame not found, create a new frame
      if (frameIndexToUpdate === -1) {
        console.log("Frame not found, creating new frame");
        return [
          ...frameList,
          {
            frameId,
            contentFrame: {} as CompletionFrameChunk,
            artifactFrames: [incomingFrame],
            thoughtFrames: [],
          } as FrameType,
        ];
      }

      const updatedFrame = {
        ...frameList[frameIndexToUpdate],
        artifactFrames: [
          ...frameList[frameIndexToUpdate].artifactFrames,
          incomingFrame,
        ],
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
