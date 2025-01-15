import { AudioTranscriber } from "../infrastructure/media/audio/AudioTranscriber";
import useMedia from "./useMedia";

type UseVoiceProps = {
  onTranscription: (transcription: string) => void;
  onError?: (error: string) => void;
};

const useVoiceTranscription = ({ onTranscription, onError }: UseVoiceProps) => {
  const {
    playbackUrl,
    isRecording,
    error,
    startRecording,
    stopRecording,
    runProcessor,
  } = useMedia({
    config: {
      mimeType: "audio/webm",
      constraints: { audio: true },
      processors: { "audio/transcriber": new AudioTranscriber() },
    },
    onError,
  });


  const transcribeAudio = async () => {
    const result = await runProcessor("audio/transcriber");
    if (result) {
      onTranscription(result.transcription);
    }
  };

  return {
    isRecording,
    error,
    startRecording,
    stopRecording,
    transcribeAudio,
    playbackUrl,
  };
};

export default useVoiceTranscription;
