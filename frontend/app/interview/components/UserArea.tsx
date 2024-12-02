import { Button } from "@/components/ui/button";
import { useWebsocketContext } from "../context/WebsocketContext";
import useVoiceTranscription from "../hooks/useVoiceTranscription";
import MessageFrame from "./MessageFrame";
import { FrameState } from "../reducers/frameReducer";
import { Mic, MicOff } from "lucide-react";
import TextareaResizable from "./TextAreaResizable";
import { useInput } from "../context/InputContext";

const AudioRecorder = () => {
  const { state: inputValue, dispatch: dispatchInputValue } = useInput();
  const { isRecording, error, startRecording, stopRecording, transcribeAudio } =
    useVoiceTranscription({
      onTranscription: (transcription) => {
        console.log(transcription);
        dispatchInputValue({
          type: "APPEND_INPUT",
          payload: transcription,
        });
      },
    });

  const handleToggleRecording = async () => {
    if (isRecording) {
      await transcribeAudio();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <Button
        onClick={handleToggleRecording}
        size="icon"
        variant={isRecording ? "destructive" : "default"}
        className="relative h-8 w-8 rounded-full"
      >
        {isRecording ? (
          <MicOff className="h-4 w-4" />
        ) : (
          <Mic className="h-4 w-4" />
        )}
        {isRecording && (
          <span className="absolute top-0 right-0 h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
        )}
      </Button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
};

const UserInput = () => {
  return (
    <TextareaResizable
      maxTextareaHeight={400}
      handleSubmit={(e) => {
        e.preventDefault();
        console.log("submitted");
      }}
    />
  );
};

const MessageContainer = ({ frames }: FrameState) => {
  return (
    <div className="flex flex-col grow gap-2 max-h-screen overflow-scroll text-sm no-scrollbar md:w-2/3 w-full items-start p-4 md:p-0">
      {frames.map((frame, index) => (
        <MessageFrame key={index} frame={frame} />
      ))}
    </div>
  );
};

const UserArea = () => {
  const { state: frameList } = useWebsocketContext();

  return (
    <div className="flex flex-col gap-2 items-center md:w-2/3 ">
      <MessageContainer frames={frameList.frames} />
      <UserInput />
      <AudioRecorder />
    </div>
  );
};

export default UserArea;
