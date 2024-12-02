import { createHumanInputFrame } from "@/app/lib/helperFunctions";
import { useInput } from "../context/InputContext";
import { useWebsocketContext } from "../context/WebsocketContext";
import AudioRecorder from "./AudioRecorder";
import TextareaResizable from "./TextAreaResizable";

type UserInputProps = {
  maxTextareaHeight: number;
};

const UserInputArea = ({ maxTextareaHeight }: UserInputProps) => {
  const { dispatch: dispatchFrame, sendMessage } = useWebsocketContext();
  const { state: inputValue, dispatch: dispatchInputValue } = useInput();

  return (
    <div className="flex w-full bg-green-200">
      <TextareaResizable
        maxTextareaHeight={maxTextareaHeight}
        handleSubmit={(e) => {
          e.preventDefault();
          const frame = createHumanInputFrame(inputValue);
          sendMessage(frame);
          dispatchFrame({ type: "ADD_FRAME", payload: frame });
          dispatchInputValue({ type: "SET_INPUT", payload: "" });
        }}
      />
      <AudioRecorder />
    </div>
  );
};

export default UserInputArea;
export type { UserInputProps };
