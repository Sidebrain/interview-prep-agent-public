import { FrameType } from "@/reducers/messageFrameReducer";
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
      <>
        <Option option={thought.options} key={idx} />
        <Suggestion suggestion={thought.sample_answer} key={idx} />
      </>
    ));
  };
  return <>{renderSuggestion(frame)}</>;
};

export default HelperContent;
