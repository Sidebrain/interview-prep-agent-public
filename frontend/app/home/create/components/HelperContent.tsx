import { FrameType } from "@/types/reducerTypes";
import Suggestion from "./Suggestion";
import Option from "./Option";
import { ThoughtSchema } from "@/types/ScalableWebsocketTypes";
import { useInput } from "@/context/InputContext";
import { useEffect, useMemo } from "react";

type HelperContentProps = {
  frame: FrameType;
};

const HelperContent = ({ frame }: HelperContentProps) => {
  const { dispatch } = useInput();

  const thoughts = useMemo(
    () =>
      frame.thoughtFrames.map((tframe) =>
        ThoughtSchema.parse(JSON.parse(tframe.content ?? ""))
      ),
    [frame.thoughtFrames]
  );

  useEffect(() => {
    let input = "";
    thoughts.forEach((thought) => {
      input += thought.userAnswer;
    });
    dispatch({ type: "SET_INPUT", payload: input });
  }, [thoughts]);

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
