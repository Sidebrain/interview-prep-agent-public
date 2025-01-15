import clientLogger from "@/app/lib/clientLogger";
import { MediaMimeType } from "./types";

export class MediaStreamRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private mimeType: MediaMimeType;
  private timeslice?: number;
  private mediaChunks: Blob[] = [];
  private playbackUrl: string | null = null;

  constructor(mimeType: MediaMimeType, timeslice?: number ) {
    this.mimeType = mimeType;
    this.timeslice = timeslice 
  }

  public isReady = () => this.mediaRecorder !== null;

  public createPlaybackUrl = () => {
    this.revokePlaybackUrl();

    if (this.mediaChunks.length === 0) {
      return null;
    }
    const mediaBlob = new Blob(this.mediaChunks, { type: this.mimeType });
    this.playbackUrl = URL.createObjectURL(mediaBlob);
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
    clientLogger.debug("MediaStreamRecorder initialized", {
      mediaRecorder: this.mediaRecorder,
      mimeType: this.mimeType,
      timeslice: this.timeslice,

    });
  };

  public startRecording = () => {
    this.mediaChunks = [];
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
        if (this.mediaChunks.length === 0) {
          clientLogger.warn("No audio chunks to stop recording");
          resolve(null);
          return;
        }
        const audioBlob = new Blob(this.mediaChunks, { type: this.mimeType });
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
    this.mediaChunks.push(event.data);
  };

  public cleanup = async () => {
    if (this.mediaRecorder?.state === "recording") {
      await this.mediaRecorder.stop();
    }
    this.mediaChunks = [];
    this.mediaRecorder = null;
    this.revokePlaybackUrl();
  };
}
