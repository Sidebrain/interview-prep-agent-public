import { createHumanInputFrame } from "@/app/lib/helperFunctions";
import { useInput } from "../context/InputContext";
import { useWebsocketContext } from "../context/WebsocketContext";
import AudioRecorder from "./AudioRecorder";
import TextareaResizable from "./TextAreaResizable";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { FormEvent, useRef } from "react";

type UserInputProps = {
  maxTextareaHeight: number;
};

const UserInputArea = ({ maxTextareaHeight }: UserInputProps) => {
  const { dispatch: dispatchFrame, sendMessage } = useWebsocketContext();
  const { state: inputValue, dispatch: dispatchInputValue } = useInput();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent<Element>) => {
    e.preventDefault();
    const frame = createHumanInputFrame(inputValue);
    sendMessage(frame);
    dispatchFrame({ type: "ADD_FRAME", payload: frame });
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  };

  return (
    <div className="flex bg-gray-50 border-t border-gray-300 p-2 rounded-md mb-2 w-full items-end justify-between">
      <AudioRecorder />
      <TextareaResizable
        maxTextareaHeight={maxTextareaHeight}
        handleSubmit={handleSubmit}
        ref={textareaRef}
      />
      <Button
        onClick={handleSubmit}
        className="p-2 rounded-full aspect-square hover:bg-primary/90 transition-colors"
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  );
};

export default UserInputArea;
export type { UserInputProps };
