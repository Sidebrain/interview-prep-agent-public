import clientLogger from "@/app/lib/clientLogger";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

export interface FrameList {
  websocketFrames: WebsocketFrame[];
}

export const initialFrameList: FrameList = {
  websocketFrames: [],
};

export type FrameAction =
  | { type: "ADD_FRAME"; payload: WebsocketFrame }
  | { type: "REMOVE_FRAME"; payload: string };

export const frameReducer = (
  state: FrameList,
  action: FrameAction
): FrameList => {
  switch (action.type) {
    case "ADD_FRAME":
      // temporary check to prevent duplicate frames
      // Duplicate check now includes address
      if (
        state.websocketFrames.find((frame) => frame.frameId === action.payload.frameId && frame.address === action.payload.address)
      ) {
        clientLogger.debug("Duplicate frame received", {
          frameId: action.payload.frameId,
        });
        return state;
      }
      return {
        ...state,
        websocketFrames: [...state.websocketFrames, action.payload],
      };
    case "REMOVE_FRAME":
      return {
        ...state,
        websocketFrames: state.websocketFrames.filter(
          (frame) => frame.frameId !== action.payload
        ),
      };
    default:
      return state;
  }
};
