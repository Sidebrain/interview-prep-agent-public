import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { frameSelectors } from "./frameSelectors";
import ConversationFrame from "../components/frames/ConversationFrame";
import EvaluationFrame from "../components/frames/EvaluationFrame";
import SuggestionFrame from "../components/frames/SuggestionFrame";
import PerspectiveFrame from "../components/frames/PerspectiveFrame";

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

  perspective: createRenderer<React.ReactNode>({
    select: frameSelectors.perspective,
    render: (frames) =>
      frames.map((frame) => (
        <PerspectiveFrame key={frame.frameId} websocketFrame={frame} />
      )),
  }),

  evaluation: createRenderer<React.ReactNode>({
    select: frameSelectors.evaluation,
    render: (frames) =>
      frames.map((frame) => (
        <EvaluationFrame key={frame.frameId} websocketFrame={frame} />
      )),
  }),

  currentSuggestion: createRenderer<React.ReactNode>({
    select: frameSelectors.lastThought,
    render: (frames) => {
      console.log("Selected suggestion frames:", {
        frames,
        length: frames.length,
        firstFrame: frames[0],
      });

      return frames.length > 0 ? (
        <SuggestionFrame websocketFrame={frames[0]} />
      ) : null;
    },
  }),
};
