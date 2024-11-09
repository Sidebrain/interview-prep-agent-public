import {
  CompletionFrameChunk,
  WebsocketFrame,
} from "@/types/ScalableWebsocketTypes";

type FrameType = {
  frameId: string;
  contentFrame: CompletionFrameChunk;
  artifactFrames: CompletionFrameChunk[];
  thoughtFrames: CompletionFrameChunk[];
};

type ActionType =
  | "heartbeat"
  | "completion/content"
  | "completion/thought"
  | "completion/artifact"
  | "streaming/content"
  | "streaming/artifact";

type Action = {
  type: ActionType;
  payload: WebsocketFrame;
};

export type { FrameType, Action, ActionType };
