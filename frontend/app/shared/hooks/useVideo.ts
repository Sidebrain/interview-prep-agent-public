import clientLogger from "@/app/lib/clientLogger";
import { VideoUploadProcessor } from "../infrastructure/media/video/VideoUploadProcessor";
import useMedia from "./useMedia";
import { SignedUrlSchema } from "../infrastructure/media/types";

type UseVideoProps = {
  videoElementRef: React.RefObject<HTMLVideoElement>;
  onError?: (error: string) => void;
  interview_session_id: string;
};

const useVideo = ({ videoElementRef, onError, interview_session_id }: UseVideoProps) => {
  const { 
    mediaService, 
    error, 
    isRecording, 
    playbackUrl, 
    runProcessor,
    ...mediaControls 
    } = useMedia({
    config: {
      mimeType: "video/webm",
      constraints: { video: true, audio: false },
      processors: {
        "video/upload": new VideoUploadProcessor(
          async () => {
            const requestBody = {
              interview_session_id: interview_session_id,
              filename: "video.webm",
              content_type: "video/webm",
            };
            clientLogger.info("Request body: ", requestBody);
            const signedUrl = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + "/api/v3/storage/generate-upload-url", {
              method: "POST",
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(requestBody),
            });
            const data = await signedUrl.json();
            const signedUrlResponse = SignedUrlSchema.parse(data);
            return signedUrlResponse;
          }
        ),
      },
    },
    onError,
  });

  const uploadVideo = async () => {
    const result = await runProcessor("video/upload");
    if (result) {
      console.log("Video uploaded", result);
    }
  };

  const startStream = async () => {
    try {
      await mediaService?.initializeMediaStream();
      const stream = mediaService?.streamManager.getStream();
      clientLogger.info("Video stream pre-started", {
        stream: stream,
      });
      if (videoElementRef.current && stream) {
        videoElementRef.current.srcObject = stream;
        clientLogger.info("Video stream started", {
          stream: stream,
        });
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
    uploadVideo,
    ...mediaControls,
  };
};

export default useVideo;
