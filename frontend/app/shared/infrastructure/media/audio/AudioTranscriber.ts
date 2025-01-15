import clientLogger from "@/app/lib/clientLogger";
import { BaseMediaProcessor, MediaProcessor, TranscriptionResult } from "../types";

export class AudioTranscriber extends BaseMediaProcessor<TranscriptionResult> {
  public process = async (media: Blob | null) => {
    if (!this.validateMedia(media)) {
      return null;
    }

    const data = new FormData();
    clientLogger.debug("Transcribing audio", {
      audioBlobSize: media.size,
      audioBlobType: media.type,
    });
    data.append("file", media, "audio.webm");

    const transcription = await this.makeTranscriptionRequest(data);
    return { transcription: transcription ?? "" };
  };


  private makeTranscriptionRequest = async (formData: FormData) => {
    try {
      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + "/api/v1/audio/transcribe",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          "Transcription request failed with status: " + response.status
        );
      }

      const transcription = (await response.json()) as string | null;
      return transcription;
    } catch (error) {
      clientLogger.error("Failed to make transcription request", {
        error: error,
      });
      throw new Error(`Failed to make transcription request: ${error}`);
    }
  };
}
