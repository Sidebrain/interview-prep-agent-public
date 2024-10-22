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

  function stopRecordingAndTranscribe(e: React.MouseEvent) {
    // e.preventDefault();
    stopRecording();
    transcribeAudio();
  }

  const renderRecordingIcon = () => {
    if (isRecording) {
      return (
        <Icons.microphoneRecording
          onClick={(e) => stopRecordingAndTranscribe(e)}
          className="h-6 w-6"
        />
      );
    }
    return (
      <Icons.microphone
        onClick={getPermissionsAndStartRecording}
        className="h-6 w-6"
      />
    );
  };

  return renderRecordingIcon();
};

export default AudioButton;
