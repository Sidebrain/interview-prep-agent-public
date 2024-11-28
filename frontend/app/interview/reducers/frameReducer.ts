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
