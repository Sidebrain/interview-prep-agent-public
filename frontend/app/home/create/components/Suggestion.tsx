import { Button } from "@/components/ui/button";
import InputContext from "@/context/InputContext";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import { FrameType } from "@/reducers/messageFrameReducer";
import { Thought, ThoughtSchema } from "@/types/ScalableWebsocketTypes";
import { CheckCircleIcon } from "lucide-react";
import { useContext, useRef } from "react";

type SuggestionProps = {
  frame: FrameType;
};

const Suggestion = ({ frame }: SuggestionProps) => {
  const { dispatch: dispatchInputValue } = useContext(InputContext);
  const suggestionRef = useRef<HTMLParagraphElement>(null);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    dispatchInputValue({
      type: "SET_INPUT",
      payload: suggestionRef.current?.textContent ?? "",
    });
  };
  const renderSuggestion = (frame: FrameType) => {
    const thoughts = frame.thoughtFrames.map((tframe) =>
      ThoughtSchema.parse(JSON.parse(tframe.content ?? ""))
    );
    return thoughts.map((tframe, idx) => (
      <div
        className="p-1 rounded-sm text-sm flex flex-col gap-2 items-start relative bg-transparent"
        key={idx}
      >
        <p className="border p-1 bg-green-600 text-sm rounded-sm text-white z-10">
          Suggestion
        </p>
        <p ref={suggestionRef} className="text-sm bg-green-200 p-2 rounded-md">
          {tframe.sample_answer}
        </p>
        <div className="flex w-full justify-end absolute bottom-0 right-0">
          <Button
            onClick={handleClick}
            variant={"outline"}
            size={"sm"}
            className="p-1"
          >
            <CheckCircleIcon className="w-4 h-4" />
          </Button>
        </div>
      </div>
    ));
  };
  return <>{renderSuggestion(frame)}</>;
};

export default Suggestion;
