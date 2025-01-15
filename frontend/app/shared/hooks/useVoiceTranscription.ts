import { AudioTranscriber } from "../infrastructure/media/audio/AudioTranscriber";
import useMedia from "./useMedia";

type UseVoiceProps = {
  onTranscription: (transcription: string) => void;
};

const useVoiceTranscription = ({ onTranscription }: UseVoiceProps) => {
  const {
    playbackUrl,
    isRecording,
    error,
    startRecording,
    stopRecording,
    runProcessor,
  } = useMedia({
    onTranscription,
    config: {
      mimeType: "audio/webm",
      constraints: { audio: true },
      processors: { "audio/transcriber": new AudioTranscriber() },
    },
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
