import clientLogger from "@/app/lib/clientLogger";

export type MediaMimeType = "audio/webm" | "video/webm" ;

export type ProcessorType = "audio/transcriber" | "video/upload";

export type MediaProcessorMap = {
    [K in ProcessorType]?: MediaProcessor<any>;
}

export interface MediaProcessor<T> {
    process: (media: Blob | null) => Promise<T | null>;
}

export interface TranscriptionResult {
    transcription: string;
}

export abstract class BaseMediaProcessor<T> implements MediaProcessor<T> {
    abstract process: (media: Blob | null) => Promise<T | null>;

    protected validateMedia = (media: Blob | null): media is Blob => {
        if (!media) {
            clientLogger.warn("No media provided to process");
            return false;
        }
        if (media.size === 0) {
            clientLogger.warn("Media is empty");
            return false;
        }
        return true;
    }
}

export interface MediaServiceConfig {
  mimeType: MediaMimeType;
  constraints: MediaStreamConstraints;
  timeslice?: number;
  processors?: MediaProcessorMap;
}

export interface MediaServiceInterface {
  initializeMediaStream: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  // transcribeAudio: (audioBlob: Blob) => Promise<string | null>;
  cleanup: () => Promise<void>;
}

import { z } from "zod";

export const SignedUrlSchema = z.object({
    url: z.string().url(),
    storage_filename: z.string(),
    expires_in: z.number().int().positive()
});

export type SignedUrlResponse = z.infer<typeof SignedUrlSchema>;
