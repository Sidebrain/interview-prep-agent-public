import clientLogger from "@/app/lib/clientLogger";

export type mimeType = "audio/webm";

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private mimeType: mimeType;
  private timeslice: number;
  private audioChunks: Blob[] = [];
  private playbackUrl: string | null = null;

  constructor(mimeType: mimeType = "audio/webm", timeslice: number = 1000) {
    this.mimeType = mimeType;
    this.timeslice = timeslice;
  }

  public isReady = () => this.mediaRecorder !== null;

  public createPlaybackUrl = () => {
    this.revokePlaybackUrl();

    if (this.audioChunks.length === 0) {
      return null;
    }
    const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
    this.playbackUrl = URL.createObjectURL(audioBlob);
    return this.playbackUrl;
  };

  private revokePlaybackUrl = () => {
    if (this.playbackUrl) {
      URL.revokeObjectURL(this.playbackUrl);
      this.playbackUrl = null;
    }
  };

  public initialize = (stream: MediaStream) => {
    this.mediaRecorder = new MediaRecorder(stream, { mimeType: this.mimeType });
    this.addEventListeners();
  };

  public startRecording = () => {
    this.audioChunks = [];
    this.mediaRecorder!.start(this.timeslice);
  };

  public stopRecording = async (): Promise<Blob | null> => {
    if (!this.isReady()) {
      throw new Error("MediaRecorder not initialized");
    }

    if (this.mediaRecorder!.state === "inactive") {
      clientLogger.warn("Attempted to stop an inactive MediaRecorder");
      return null;
    }

    return new Promise<Blob | null>((resolve) => {
      this.mediaRecorder!.onstop = () => {
        if (this.audioChunks.length === 0) {
          clientLogger.warn("No audio chunks to stop recording");
          resolve(null);
          return;
        }
        const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
        resolve(audioBlob);
      };
      this.mediaRecorder!.stop();
    });
  };

  public addEventListeners = () => {
    this.mediaRecorder!.ondataavailable = this.handleDataAvailable;
  };

  public removeEventListeners = () => {
    this.mediaRecorder!.ondataavailable = null;
  };

  private handleDataAvailable = (event: BlobEvent) => {
    this.audioChunks.push(event.data);
  };

  public cleanup = async () => {
    if (this.mediaRecorder?.state === "recording") {
      await this.mediaRecorder.stop();
    }
    this.audioChunks = [];
    this.mediaRecorder = null;
    this.revokePlaybackUrl();
  };
}
