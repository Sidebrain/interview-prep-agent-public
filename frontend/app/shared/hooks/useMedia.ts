import clientLogger from "@/app/lib/clientLogger";
import { useEffect, useRef, useState } from "react";
import { MediaService } from "../infrastructure/media/MediaService";
import { MediaServiceConfig, ProcessorType } from "../infrastructure/media/types";

type UseMediaProps = {
  config: MediaServiceConfig;
  onError?: (error: string) => void;
};

const useMedia = ({
  config,
  onError,
}: UseMediaProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaServiceRef = useRef<MediaService | null>(null);
  const [playbackUrl, setPlaybackUrl] = useState<string | null>(null);
  const [mediaBlob, setMediaBlob] = useState<Blob | null>(null);
  const initializingRef = useRef(false);

  useEffect(() => {
    if (!mediaServiceRef.current && !initializingRef.current) {
      mediaServiceRef.current = new MediaService(config);
    }

    return () => {
      if (mediaServiceRef.current) {
        mediaServiceRef.current.cleanup();
        mediaServiceRef.current = null;
      }
    };
  }, []);

  const handleError = (error: unknown) => {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    setError(errorMessage);
    onError?.(errorMessage);
    clientLogger.error("Media service error: ", errorMessage);
  };

  const startRecording = async () => {
    try {
      if (initializingRef.current) return;
      initializingRef.current = true;
      
      setIsRecording(true);
      setError(null);
      await getMediaService().startRecording();
    } catch (error) {
      handleError(error);
    } finally {
      initializingRef.current = false;
    }
  };

  const getMediaService = () => {
    const mediaService = mediaServiceRef.current;
    if (!mediaService) {
      throw new Error("Media service not initialized");
    }
    return mediaService;
  };

  const stopRecording = async () => {
    try {
      const mediaService = getMediaService();
      const mediaBlob = await mediaService.stopRecording();
      setMediaBlob(mediaBlob);
      setPlaybackUrl(mediaService.createPlaybackUrl());
    } catch (error) {
      handleError(error);
    } finally {
      setIsRecording(false);
    }
  };

  const runProcessor = async (processorKey: ProcessorType) => {
    try {
        const mediaService = getMediaService();
        let blob = mediaBlob;
        
        if (isRecording) {
            blob = await mediaService.stopRecording();
            setIsRecording(false);
            setMediaBlob(blob);
            setPlaybackUrl(mediaService.createPlaybackUrl());
        }

        if (!blob) {
            throw new Error("No media blob available");
        }

        return await mediaService.runProcessor(blob, processorKey);
        } catch (error) {
        handleError(error);
        }
  };


  return {
    isRecording,
    error,
    startRecording,
    stopRecording,
    playbackUrl,
    runProcessor,
    mediaService: mediaServiceRef.current,
    mediaBlob
  };
};

export default useMedia;
