import { FrameType } from "@/types/reducerTypes";
import Suggestion from "./Suggestion";
import Option from "./Option";
import { ThoughtSchema } from "@/types/ScalableWebsocketTypes";
import { useMemo } from "react";

type HelperContentProps = {
  frame: FrameType;
};

const HelperContent = ({ frame }: HelperContentProps) => {

  const thoughts = useMemo(
    () =>
      frame.thoughtFrames.map((tframe) =>
        ThoughtSchema.parse(JSON.parse(tframe.content ?? ""))
      ),
    [frame.thoughtFrames]
  );

  return (
    <>
      {thoughts.map((thought, idx) => (
        <div key={`thought-${idx}`}>
          <Option option={thought.options} />
          <Suggestion suggestion={thought.sampleAnswer} />
        </div>
      ))}
    </>
  );
};

export default HelperContent;
