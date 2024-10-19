import { useRef, useState } from "react";
import { useEffect } from "react";
import { useCallback } from "react";
import clientLogger from "../lib/clientLogger";
import { transcribeAudioChunks } from "@/components/AiGeneratedSection/actions";
import { on } from "events";

type VoiceHookParams = {
  chunkSize?: number;
  maxRecordingTime?: number;
  onTranscription?: (transcription: string) => void;
};

const useVoice = (props: VoiceHookParams) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const getPermissions = useCallback(async () => {
    if (!streamRef.current) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        streamRef.current = stream;
      } catch (err) {
        setError("Failed to get audio permissions");
        clientLogger.error("Failed to get audio permissions", err);
        throw err;
      }
    }
  }, [setError]);

  const startRecording = useCallback(() => {
    if (streamRef.current) {
      mediaRecorderRef.current = new MediaRecorder(streamRef.current, {
        mimeType: "audio/webm",
      });

      // Reset the audio chunks
      setAudioChunks([]);

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setAudioChunks((prev) => [...prev, event.data]);
          // Do something with the audio chunks here like sending them to a server for transcription
          clientLogger.debug("event data", event.data);
          clientLogger.debug("Audio chunks recorded: ", audioChunks);
        }
      };

      mediaRecorderRef.current.start(props.chunkSize || 1000);
      setIsRecording(true);

      // Automatically stop recording after 5 minutes
      setTimeout(() => {
        if (isRecording) {
          stopRecording();
        }
      }, props.maxRecordingTime || 5 * 60 * 1000); // 5 minutes in milliseconds
    } else {
      setError("No audio stream available");
    }
  }, [
    props.chunkSize,
    props.maxRecordingTime,
    isRecording,
    setError,
    audioChunks,
    setAudioChunks,
  ]);

  const getPermissionsAndStartRecording = useCallback(async () => {
    try {
      await getPermissions();
      startRecording();
    } catch (err) {
      // Handle error if needed
    }
  }, [getPermissions, startRecording]);

  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive" &&
      isRecording
    ) {
      clientLogger.debug("from within useVoice stopRecording");
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clientLogger.debug("Recording stopped", audioChunks);
    } else {
      setError("No recording in progress");
      clientLogger.error("No recording in progress");
    }
  }, [setError, isRecording]);

  const playRecording = useCallback(() => {
    clientLogger.debug("Playing recording");
    clientLogger.debug("Audio chunks recorded: ", audioChunks);
    clientLogger.debug("Audio chunks of length recorded: ", audioChunks.length);
    if (audioChunks.length) {
      const audioBlob = new Blob(audioChunks, {
        type: "audio/webm",
      });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } else {
      setError("No audio chunks recorded");
      clientLogger.error("No audio chunks recorded");
    }
  }, [audioChunks]);

  const stopPlaying = useCallback(() => {
    const audio = document.querySelector("audio");
    if (audio) {
      audio.pause();
    }
  }, []);

  const transcribeAudioChunk = useCallback(async (chunk: Blob) => {
    const data = new FormData();
    data.append("file", chunk, "chunk.webm");

    try {
      const response = await transcribeAudioChunks(data);
      console.log("response", response);
      clientLogger.debug("Transcription response: ", response);
      if (props.onTranscription) props.onTranscription(response.transcription);
    } catch (err) {
      clientLogger.error(
        "something went wrong with transcribing the audio chunks",
        err
      );
      setError("Failed to transcribe audio chunks");
    }
  }, []);

  return {
    isRecording,
    error,
    getPermissionsAndStartRecording,
    stopRecording,
    playRecording,
    stopPlaying,
    transcribeAudioChunk,
    audioChunks,
    // other returned values and functions
  };
};

export default useVoice;
