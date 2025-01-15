import clientLogger from "@/app/lib/clientLogger";
import { StreamManager } from "./StreamManager";
import { AudioRecorder, mimeType } from "./AudioRecorder";
import { AudioTranscriber } from "./AudioTranscriber";

export interface AudioServiceInterface {
  initializeAudioStream: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  transcribeAudio: (audioBlob: Blob) => Promise<string | null>;
  cleanup: () => Promise<void>;
}

export class AudioService implements AudioServiceInterface {
  private streamManager: StreamManager;
  private audioRecorder: AudioRecorder;
  private audioTranscriber: AudioTranscriber;

  constructor(mimeType: mimeType = "audio/webm", timeslice: number = 1000) {
    this.streamManager = new StreamManager();
    this.audioRecorder = new AudioRecorder(mimeType, timeslice);
    this.audioTranscriber = new AudioTranscriber();
  }

  public initializeAudioStream = async () => {
    await this.streamManager.initialize();
    const stream = this.streamManager.getStream();
    if (!stream) {
      throw new Error("Failed to get audio stream");
    }
    this.audioRecorder.initialize(stream);
  };

  public isReady = () =>
    this.streamManager.isReady() && this.audioRecorder.isReady();

  public startRecording = async () => {
    if (!this.isReady()) {
      await this.initializeAudioStream();
    }
    this.audioRecorder.startRecording();
  };

  public stopRecording = async (): Promise<Blob | null> => {
    const audioBlob = await this.audioRecorder.stopRecording();
    // give up held resources so mic is not flashing red and battery is not drained
    await this.cleanup();
    return audioBlob;
  };

  public createPlaybackUrl = () => this.audioRecorder.createPlaybackUrl();

  public transcribeAudio = async (audioBlob: Blob | null) => {
    if (!audioBlob) {
      clientLogger.warn("No audio blob provided to transcribe");
      return null;
    }
    const transcription = await this.audioTranscriber.transcribeAudio(
      audioBlob
    );
    return transcription;
  };

  public cleanup = async () => {
    await this.streamManager.cleanup();
    await this.audioRecorder.cleanup();
  };
}
