import clientLogger from "@/app/lib/clientLogger";
import { StreamManager } from "./StreamManager";
import { AudioTranscriber } from "./audio/AudioTranscriber";
import { MediaStreamRecorder } from "./MediaStreamRecorder";
import { MediaMimeType } from "./types";

export interface MediaServiceConfig {
  mimeType: MediaMimeType;
  constraints: MediaStreamConstraints;
  timeslice?: number;
  transcriber?: AudioTranscriber;
}

export interface MediaServiceInterface {
  initializeMediaStream: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  // transcribeAudio: (audioBlob: Blob) => Promise<string | null>;
  cleanup: () => Promise<void>;
}

export class MediaService implements MediaServiceInterface {
  private streamManager: StreamManager;
  private recorder: MediaStreamRecorder;
  private transcriber?: AudioTranscriber;

  constructor({ 
    mimeType = "audio/webm", 
    constraints = {audio: true}, 
    timeslice, 
    transcriber 
  }: MediaServiceConfig) {
    this.streamManager = new StreamManager(constraints);
    this.recorder = new MediaStreamRecorder(mimeType, timeslice);
    this.transcriber = transcriber;
  }

  public initializeMediaStream = async () => {
    await this.streamManager.initialize();
    const stream = this.streamManager.getStream();
    if (!stream) {
      throw new Error("Failed to get audio stream");
    }
    this.recorder.initialize(stream);
  };

  public isReady = () =>
    this.streamManager.isReady() && this.recorder.isReady();

  public startRecording = async () => {
    if (!this.isReady()) {
      await this.initializeMediaStream();
    }
    this.recorder.startRecording();
  };

  public stopRecording = async (): Promise<Blob | null> => {
    const mediaBlob = await this.recorder.stopRecording();
    // give up held resources so mic is not flashing red and battery is not drained
    await this.cleanup();
    return mediaBlob;
  };

  public createPlaybackUrl = () => this.recorder.createPlaybackUrl();

  public transcribeAudio = async (mediaBlob: Blob | null) => {
    if (!this.transcriber) {
      clientLogger.warn("No transcriber provided");
      return null;
    }
    if (!mediaBlob) {
      clientLogger.warn("No audio blob provided to transcribe");
      return null;
    }
    const transcription = await this.transcriber.transcribeAudio(
      mediaBlob
    );
    return transcription;
  };

  public cleanup = async () => {
    await this.streamManager.cleanup();
    await this.recorder.cleanup();
  };
}
