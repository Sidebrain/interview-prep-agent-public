import clientLogger from "@/app/lib/clientLogger";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

export interface FrameState {
  frames: WebsocketFrame[];
}

export const initialFrameState: FrameState = {
  frames: [],
};

export type FrameAction =
  | { type: "ADD_FRAME"; payload: WebsocketFrame }
  | { type: "REMOVE_FRAME"; payload: string };

export const frameReducer = (
  state: FrameState,
  action: FrameAction
): FrameState => {
  switch (action.type) {
    case "ADD_FRAME":
      // temporary check to prevent duplicate frames
      if (
        state.frames.find((frame) => frame.frameId === action.payload.frameId)
      ) {
        clientLogger.debug("Duplicate frame received", {
          frameId: action.payload.frameId,
        });
        return state;
      }
      return {
        ...state,
        frames: [...state.frames, action.payload],
      };
    case "REMOVE_FRAME":
      return {
        ...state,
        frames: state.frames.filter(
          (frame) => frame.frameId !== action.payload
        ),
      };
    default:
      return state;
  }
};
