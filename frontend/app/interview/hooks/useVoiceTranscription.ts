import clientLogger from "@/app/lib/clientLogger";
import { AudioService } from "@/infrastructure/AudioService";
import { useEffect, useRef, useState } from "react";

type UseVoiceProps = {
  onTranscription: ({ transcription }: { transcription: string }) => void;
};

const useVoiceTranscription = ({ onTranscription }: UseVoiceProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioServiceRef = useRef<AudioService | null>(null);
  const [playbackUrl, setPlaybackUrl] = useState<string | null>(null);

  useEffect(() => {
    audioServiceRef.current = new AudioService("audio/webm");

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
      await audioService.stopRecording();
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
    try {
      const transcription = await audioService.transcribeAudio();
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
