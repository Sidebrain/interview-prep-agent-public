import clientLogger from "@/app/lib/clientLogger";
import { useEffect, useRef, useState } from "react";
import { MediaService } from "../infrastructure/media/MediaService";
import { AudioTranscriber } from "../infrastructure/media/audio/AudioTranscriber";

type UseVoiceProps = {
  onTranscription: (transcription: string) => void;
};

const useVoiceTranscription = ({ onTranscription }: UseVoiceProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioServiceRef = useRef<MediaService | null>(null);
  const [playbackUrl, setPlaybackUrl] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);

  useEffect(() => {
    audioServiceRef.current = new MediaService({
      mimeType: "audio/webm",
      constraints: { audio: true },
      processors: { "audio/transcriber": new AudioTranscriber() },
    });

    return () => {
      audioServiceRef.current?.cleanup();
    };
  }, []);

  const startRecording = async () => {
    const audioService = audioServiceRef.current;
    if (!audioService) {
      throw new Error("Audio service not initialized");
    }
    try {
      setIsRecording(true);
      setError(null);
      await audioService.startRecording();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unknown error");
    }
  };

  const stopRecording = async () => {
    const audioService = audioServiceRef.current;
    if (!audioService) {
      throw new Error("Audio service not initialized");
    }
    try {
      setIsRecording(false);
      const audioBlob = await audioService.stopRecording();
      setAudioBlob(audioBlob);
      setPlaybackUrl(audioService.createPlaybackUrl());
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsRecording(false);
    }
  };

  const transcribeAudio = async () => {
    const audioService = audioServiceRef.current;
    if (!audioService) {
      throw new Error("Audio service not initialized");
    }
    let blob = audioBlob;
    if (isRecording) {
      blob = await audioService.stopRecording();
      setIsRecording(false);
      setAudioBlob(blob);
      setPlaybackUrl(audioService.createPlaybackUrl());
    }

    try {
      const { transcription } = await audioService.runProcessor(blob, "audio/transcriber");
      if (!transcription) {
        clientLogger.warn("No transcription to return");
        return;
      }
      clientLogger.debug("Transcription response: ", transcription);
      onTranscription(transcription);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unknown error");
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
