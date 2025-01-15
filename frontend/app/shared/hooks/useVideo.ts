import useMedia from "./useMedia";

type UseVideoProps = {
  videoElementRef: React.RefObject<HTMLVideoElement>;
  onError?: (error: string) => void;
};

const useVideo = ({ videoElementRef, onError }: UseVideoProps) => {
  const { 
    mediaService, 
    error, 
    isRecording, 
    playbackUrl, 
    ...mediaControls 
    } = useMedia({
    config: {
      mimeType: "video/webm",
      constraints: { video: true, audio: false },
      processors: {},
    },
    onError,
  });

  const startStream = async () => {
    try {
      await mediaService?.initializeMediaStream();
      const stream = mediaService?.streamManager.getStream();
      
      if (videoElementRef.current && stream) {
        videoElementRef.current.srcObject = stream;
      } else {
        throw new Error("Failed to get video stream");
      }
    } catch (error) {
      onError?.(error instanceof Error ? error.message : "Unknown error");
    }
  };

  const stopStream = async () => {
    if (videoElementRef.current) {
      videoElementRef.current.srcObject = null;
    }
    await mediaService?.cleanup();
  };

  return {
    isRecording,
    error,
    playbackUrl,
    startStream,
    stopStream,
    ...mediaControls,
  };
};

export default useVideo;
