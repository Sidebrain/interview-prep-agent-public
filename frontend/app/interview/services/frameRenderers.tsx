import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { frameSelectors } from "./frameSelectors";
import ConversationFrame from "../components/frames/ConversationFrame";
import EvaluationFrame from "../components/frames/EvaluationFrame";

type FrameRenderer<T> = {
  select: (frames: WebsocketFrame[]) => WebsocketFrame[];
  render: (frames: WebsocketFrame[]) => T;
};

export const createRenderer = <T,>(renderer: FrameRenderer<T>) => {
  return (frames: WebsocketFrame[]) => {
    const selectedFrames = renderer.select(frames);
    return renderer.render(selectedFrames);
  };
};

export const frameRenderers = {
  conversation: createRenderer<React.ReactNode>({
    select: frameSelectors.conversation,
    render: (frames) =>
      frames.map((frame) => (
        <ConversationFrame key={frame.frameId} websocketFrame={frame} />
      )),
  }),

  evaluation: createRenderer<React.ReactNode>({
    select: frameSelectors.evaluation,
    render: (frames) =>
      frames.map((frame) => (
        <EvaluationFrame key={frame.frameId} websocketFrame={frame} />
      )),
  }),
};
