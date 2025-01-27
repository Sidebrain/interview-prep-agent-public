import { createHumanInputFrame } from "@/app/lib/helperFunctions";
import { useInput } from "../context/InputContext";
import { useWebsocketContext } from "../context/WebsocketContext";
import AudioRecorder from "./AudioRecorder";
import TextareaResizable from "./TextAreaResizable";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { FormEvent, useRef } from "react";
import clientLogger from "@/app/lib/clientLogger";
import { TooltipProvider } from "@/components/ui/tooltip";

type UserInputProps = {
  maxTextareaHeight: number;
};

const UserInputArea = ({ maxTextareaHeight }: UserInputProps) => {
  const { dispatch: dispatchFrame, sendMessage } =
    useWebsocketContext();
  const { state: inputValue, dispatch: dispatchInputValue } =
    useInput();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent<Element>) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    const frame = createHumanInputFrame(inputValue);
    clientLogger.debug("Sending human input frame with content", {
      content: inputValue,
      frame,
    });
    sendMessage(frame);
    dispatchFrame({ type: "ADD_FRAME", payload: frame });
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  };

  return (
    <div className="container max-w-3xl mx-auto">
      <div className="flex gap-2 bg-muted">
        <TextareaResizable
          maxTextareaHeight={maxTextareaHeight}
          handleSubmit={handleSubmit}
          ref={textareaRef}
        />
        <div className="flex flex-col gap-2">
          <TooltipProvider>
            <AudioRecorder />
          </TooltipProvider>
          {/* <Button
            variant="default"
            size="icon"
            onClick={handleSubmit}
            disabled={!inputValue.trim()}
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button> */}
        </div>
      </div>
    </div>
  );
};

export default UserInputArea;
export type { UserInputProps };
