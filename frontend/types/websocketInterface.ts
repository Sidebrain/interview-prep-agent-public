import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { Action, FrameType } from "@/types/reducerTypes";

type WebsocketInterface = {
  sendMessage: (data: WebsocketFrame) => void;
  readyState: number;
  connectionStatus: string;
  frameList: FrameType[];
  dispatch: React.Dispatch<Action>;
  frameHandler: (frame: WebsocketFrame) => void;
  createHumanInputFrame: (content: string) => WebsocketFrame;
};

export type { WebsocketInterface };
