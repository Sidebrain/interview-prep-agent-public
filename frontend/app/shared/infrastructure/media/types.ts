import clientLogger from "@/app/lib/clientLogger";

export type MediaMimeType = "audio/webm" | "video/webm" 

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