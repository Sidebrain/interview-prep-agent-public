import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { Action, FrameType } from "@/types/reducerTypes";
import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";

type WebsocketInterface = {
  sendMessage: (data: WebsocketFrame) => void;
  readyState: number;
  connectionStatus: string;
  frameList: FrameType[];
  dispatch: React.Dispatch<Action>;
  frameHandler: (frame: WebsocketFrame) => void;
  createHumanInputFrame: (content: string) => WebsocketFrame;
  createRegenerateSignalFrame: (
    frameToRegenerate: CompletionFrameChunk
  ) => WebsocketFrame;
};

export type { WebsocketInterface };
