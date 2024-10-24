import { Icons } from "@/components/icons";
import InputContext from "@/context/InputContext";
import useVoice from "@/hooks/useVoice";
import React, { useContext } from "react";

const AudioButton = () => {
  const { dispatch: dispatchInputValue } = useContext(InputContext);
  const {
    getPermissionsAndStartRecording,
    stopRecording,
    isRecording,
    transcribeAudio,
  } = useVoice({
    onTranscription: (transcription) => {
      dispatchInputValue({ type: "APPEND_INPUT", payload: transcription });
    },
  });

  async function stopRecordingAndTranscribe(e: React.MouseEvent) {
    // e.preventDefault();
    await stopRecording();
    await transcribeAudio();
  }

  const renderRecordingIcon = () => {
    if (isRecording) {
      return (
        <div
          onClick={(e) => stopRecordingAndTranscribe(e)}
          className="relative rounded-full p-2 inline-flex items-center justify-center"
        >
          <>
            <span className="absolute inline-flex h-full w-full animate-ping opacity-75 rounded-full bg-red-600" />
            <span className="absolute inline-flex h-[120%] w-[120%] animate-ping animation-delay-150 opacity-50 rounded-full bg-red-600" />
          </>
          <Icons.microphoneRecording className="h-4 w-4" />
        </div>
      );
    }
    return (
      <div className="relative bg-gray-300 rounded-full p-2 inline-flex items-center justify-center">
        <Icons.microphone
          onClick={getPermissionsAndStartRecording}
          className="h-4 w-4 "
        />
      </div>
    );
  };

  return renderRecordingIcon();
};

export default AudioButton;
