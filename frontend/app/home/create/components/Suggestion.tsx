import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import { FrameType } from "@/reducers/messageFrameReducer";
import { Thought, ThoughtSchema } from "@/types/ScalableWebsocketTypes";

type SuggestionProps = {
  frame: FrameType;
};

const Suggestion = ({ frame }: SuggestionProps) => {
  const renderSuggestion = (frame: FrameType) => {
    // return frameRenderHandler({ frame: frame, address: "thought" });
    const thoughts = frame.thoughtFrames.map((tframe) =>
      ThoughtSchema.parse(JSON.parse(tframe.content ?? ""))
    );
    return thoughts.map((tframe, idx) => (
      <div className="p-4 m-2 rounded-sm text-sm bg-green-200" key={idx}>
        {tframe.sample_answer}
      </div>
    ));
  };
  return <>{renderSuggestion(frame)}</>;
};

export default Suggestion;
