import { Mic } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInput } from "../context/InputContext";
import useVoiceTranscription from "../hooks/useVoiceTranscription";
import { MicOff } from "lucide-react";

const AudioRecorder = () => {
  const { dispatch: dispatchInputValue } = useInput();
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

export default AudioRecorder;
