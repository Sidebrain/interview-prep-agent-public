import { Key, Mic, Keyboard, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useInput } from "../context/InputContext";
import useVoiceTranscription from "../hooks/useVoiceTranscription";
import { TooltipContent } from "@/components/ui/tooltip";
import { TooltipTrigger } from "@/components/ui/tooltip";
import { Tooltip } from "@/components/ui/tooltip";

const AudioRecorder = () => {
  const { dispatch: dispatchInputValue } = useInput();
  const {
    isRecording,
    error,
    startRecording,
    transcribeAudio,
  } = useVoiceTranscription({
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
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4 min-h-[80px] bg-muted rounded-md p-4">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="icon" onClick={() => {}}>
              <Keyboard className="h-4 w-4" />
              <span className="sr-only">Switch to text input</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>Switch to text input</TooltipContent>
        </Tooltip>
        <Button
          variant={isRecording ? "destructive" : "default"}
          size="icon"
          onClick={handleToggleRecording}
        >
          {isRecording ? (
            <X className="h-4 w-4 animate-pulse" />
          ) : (
            <Mic className="h-4 w-4" />
          )}
          <span className="sr-only">
            {isRecording ? "Stop recording" : "Start recording"}
          </span>
        </Button>
      </div>
      {/* <AudioVisualizer isRecording={isRecording} /> */}
    </div>
  );

  // return (
  //   <div className="flex flex-col items-center gap-2">
  //     <Button
  //       onClick={handleToggleRecording}
  //       size="icon"
  //       variant={isRecording ? "destructive" : "default"}
  //       className="relative h-8 w-8 rounded-full"
  //     >
  //       {isRecording ? (
  //         <MicOff className="h-4 w-4" />
  //       ) : (
  //         <Mic className="h-4 w-4" />
  //       )}
  //       {isRecording && (
  //         <span className="absolute top-0 right-0 h-3 w-3">
  //           <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
  //           <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
  //         </span>
  //       )}
  //     </Button>
  //     {error && <p className="text-red-500 text-sm">{error}</p>}
  //   </div>
  // );
};

export default AudioRecorder;
