import clientLogger from "@/app/lib/clientLogger";

export interface AudioServiceInterface {
  initializeAudioStream: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  transcribeAudio: () => Promise<{ transcription: string }>;
}

export class AudioService implements AudioServiceInterface {
  // #region Properties
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;
  private audioChunks: Blob[] = [];
  private mimeType: string;
  // #endregion Properties

  // #region Constructor
  constructor(mimeType: string) {
    this.mimeType = mimeType;
  }
  // #endregion Constructor

  // #region Public Methods
  public initializeAudioStream = async () => {
    const audioStream = await this.requestAudioStream();
    this.stream = audioStream;
  };

  public startRecording = async () => {
    await this.ensureStreamIsReady();
    this.mediaRecorder = this.createMediaRecorder();
    this.cleanupData();
    this.mediaRecorder.start();
  };

  public stopRecording = async () => {
    if (!this.isStreamReady() || !this.isRecording()) {
      throw new Error("Cannot stop recording: No active recording found");
    }

    this.mediaRecorder!.stop();
  };

  public cleanup = async () => {
    this.cleanupMediaRecorder();
    this.cleanupStream();
    this.cleanupData();
  };

  public transcribeAudio = async () => {
    const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
    const data = new FormData();
    data.append("file", audioBlob, "audio.webm");

    const transcription = await this.makeTranscriptionRequest(data);
    return transcription;
  };
  // #endregion Public Methods

  // #region Stream Management
  private requestAudioStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      clientLogger.debug("Audio permissions granted", {
        stream: stream,
      });

      return stream;
    } catch (error) {
      clientLogger.error("Failed to get audio permissions", error);
      throw error;
    }
  };

  private ensureStreamIsReady = async () => {
    if (!this.isStreamReady()) {
      await this.initializeAudioStream();
    }
  };

  private isStreamAvailable = () => Boolean(this.stream);

  private isStreamActive = () => this.stream?.active ?? false;

  private isStreamReady = () => {
    return this.isStreamAvailable() && this.isStreamActive();
  };

  private cleanupStream = () => {
    if (this.stream) {
      this.removeTracks();
      this.stream = null;
    }
  };

  private removeTracks = () => {
    this.stream!.getTracks().forEach((track) => {
      track.stop();
      track.enabled = false;
    });
  };
  // #endregion Stream Management

  // #region Recording Management
  private createMediaRecorder = () => {
    if (!this.isStreamReady()) {
      throw new Error("No stream available");
    }

    try {
      const mediaRecorder = new MediaRecorder(this.stream!, {
        mimeType: this.mimeType,
      });
      this.addEventListeners();
      return mediaRecorder;
    } catch (error) {
      clientLogger.error("Failed to create MediaRecorder", {
        error: error,
        mimeType: this.mimeType,
      });
      throw error;
    }
  };

  private addEventListeners = () => {
    this.mediaRecorder!.ondataavailable = this.handleDataAvailable;
  };

  private removeEventListeners = () => {
    this.mediaRecorder!.ondataavailable = null;
  };

  private cleanupMediaRecorder = () => {
    if (this.isRecording()) {
      this.stopRecording();
    }

    if (this.mediaRecorder) {
      this.removeEventListeners();
      this.mediaRecorder = null;
    }
  };

  private cleanupData = () => {
    this.audioChunks = [];
  };

  private handleDataAvailable = (event: BlobEvent) => {
    this.audioChunks.push(event.data);
  };

  private isRecording = () => {
    return this.mediaRecorder?.state === "recording";
  };
  // #endregion Recording Management

  // #region Transcription Management
  private makeTranscriptionRequest = async (formData: FormData) => {
    try {
      const response = await fetch(
        process.env.BACKEND_URL + "/api/v1/audio/transcribe",
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

      const transcription = (await response.json()) as {
        transcription: string;
      };

      return transcription;
    } catch (error) {
      clientLogger.error("Failed to make transcription request", {
        error: error,
      });
      throw new Error(`Failed to make transcription request: ${error}`);
    }
  };
  // #endregion Transcription Management
}
