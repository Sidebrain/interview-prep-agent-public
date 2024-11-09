import { FrameType } from "@/types/reducerTypes";
import Suggestion from "./Suggestion";
import Option from "./Option";
import { ThoughtSchema } from "@/types/ScalableWebsocketTypes";

type HelperContentProps = {
  frame: FrameType;
};

const HelperContent = ({ frame }: HelperContentProps) => {
  const renderSuggestion = (frame: FrameType) => {
    const thoughts = frame.thoughtFrames.map((tframe) =>
      ThoughtSchema.parse(JSON.parse(tframe.content ?? ""))
    );
    return thoughts.map((thought, idx) => (
      <div key={`thought-${idx}`}>
        <Option option={thought.options} />
        <Suggestion suggestion={thought.sample_answer} />
      </div>
    ));
  };
  return <>{renderSuggestion(frame)}</>;
};

export default HelperContent;
