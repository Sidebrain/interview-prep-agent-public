import clientLogger from "@/app/lib/clientLogger";

export class AudioTranscriber {
  public transcribeAudio = async (audioBlob: Blob) => {
    if (!this.validateAudioBlob(audioBlob)) {
      return null;
    }

    const data = new FormData();
    clientLogger.debug("Transcribing audio", {
      audioBlobSize: audioBlob.size,
      audioBlobType: audioBlob.type,
    });
    data.append("file", audioBlob, "audio.webm");

    const transcription = await this.makeTranscriptionRequest(data);
    return transcription;
  };

  private validateAudioBlob = (audioBlob: Blob) => {
    if (!audioBlob) {
      clientLogger.warn("No audio blob provided to transcribe");
      return false;
    }

    if (audioBlob.size === 0) {
      clientLogger.warn("Audio blob is empty");
      return false;
    }

    return true;
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
