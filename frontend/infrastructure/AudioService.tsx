import clientLogger from "@/app/lib/clientLogger";

export interface AudioServiceInterface {
  initializeAudioStream: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  transcribeAudio: () => Promise<{ transcription: string }>;
  cleanup: () => Promise<void>;
}

type mimeType = "audio/webm";

export class AudioService implements AudioServiceInterface {
  // #region Properties
  private mediaRecorder: MediaRecorder | null = null;
  private stream: MediaStream | null = null;
  private audioChunks: Blob[] = [];
  private mimeType: mimeType;
  private playbackUrl: string | null = null;
  private timeslice: number;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private isAudioActive = false;
  // #endregion Properties

  // #region Constructor
  constructor(mimeType: mimeType, timeslice: number = 1000) {
    this.mimeType = mimeType;
    this.timeslice = timeslice;
  }
  // #endregion Constructor

  // #region Public Methods
  public initializeAudioStream = async () => {
    const audioStream = await this.requestAudioStream();
    this.stream = audioStream;
  };

  public startRecording = async () => {
    await this.initializeRecordingPipeline();

    // Check audio track state
    const audioTrack = this.stream?.getAudioTracks()[0];
    clientLogger.debug("Audio track state", {
      label: audioTrack?.label,
      enabled: audioTrack?.enabled,
      muted: audioTrack?.muted,
      readyState: audioTrack?.readyState,
      constraints: audioTrack?.getConstraints(),
      settings: audioTrack?.getSettings(),
    });

    this.setupAudioAnalysis();
    this.cleanupData();

    this.mediaRecorder!.start(this.timeslice);
  };

  public stopRecording = async () => {
    if (!this.isStreamReady() || !this.isRecording()) {
      throw new Error("Cannot stop recording: No active recording found");
    }

    return new Promise<void>((resolve) => {
      this.mediaRecorder!.onstop = () => {
        this.cleanupAudioAnalysis();
        this.releaseStream();
        this.releaseRecordingPipeline();
        requestAnimationFrame(() => resolve());
      };
      this.mediaRecorder!.stop();
    });
  };

  public cleanup = async () => {
    this.cleanupMediaRecorder();
    this.cleanupAudioAnalysis();
    this.releaseStream();
    this.cleanupData();
    this.cleanupPlaybackUrl();
  };

  public transcribeAudio = async () => {
    const data = new FormData();
    const audioBlob = this.createAudioBlob();
    clientLogger.debug("Transcribing audio", {
      audioBlobSize: audioBlob.size,
      audioBlobType: audioBlob.type,
    });
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

  private releaseStream = () => {
    if (this.stream) {
      this.removeTracks();
      this.stream = null;
    }
  };

  private removeTracks = () => {
    this.stream!.getTracks().forEach((track) => {
      track.stop();
      //   track.enabled = false;
    });
  };

  private initializeRecordingPipeline = async () => {
    await this.initializeAudioStream();
    await this.initializeMediaRecorder(); // includes event listeners
  };

  private releaseRecordingPipeline = () => {
    if (!this.stream) {
      return;
    }
    this.stopTracks();
    this.mediaRecorder = null;
  };

  // #endregion Stream Management

  // #region Recording Management
  private initializeMediaRecorder = () => {
    this.mediaRecorder = this.createMediaRecorder(); // also attaches event listeners
  };

  private ensureMediaRecorderIsInitialized = async () => {
    if (!this.mediaRecorder) {
      await this.initializeMediaRecorder();
    }
  };

  private createMediaRecorder = () => {
    if (!this.isStreamReady()) {
      throw new Error("No stream available");
    }

    try {
      const mediaRecorder = new MediaRecorder(this.stream!, {
        mimeType: this.mimeType,
      });
      this.addEventListeners(mediaRecorder);
      return mediaRecorder;
    } catch (error) {
      clientLogger.error("Failed to create MediaRecorder", {
        error: error,
        mimeType: this.mimeType,
        stream: this.stream,
        mediaRecorder: this.mediaRecorder,
      });
      throw error;
    }
  };

  private addEventListeners = (mediaRecorder: MediaRecorder) => {
    mediaRecorder.ondataavailable = this.handleDataAvailable;
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

  private cleanupPlaybackUrl = () => {
    if (this.playbackUrl) {
      URL.revokeObjectURL(this.playbackUrl);
      this.playbackUrl = null;
    }
  };

  private createAudioBlob = () => {
    const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
    clientLogger.debug("Created audio blob", {
      audioChunksLength: this.audioChunks.length,
      mimeType: this.mimeType,
      audioBlobSize: audioBlob.size,
      audioBlobType: audioBlob.type,
    });
    return audioBlob;
  };

  public createPlaybackUrl = () => {
    clientLogger.debug("Creating playback URL", {
      audioChunksLength: this.audioChunks.length,
    });
    if (this.audioChunks.length === 0) {
      return null;
    }

    this.cleanupPlaybackUrl();
    const audioBlob = this.createAudioBlob();
    this.playbackUrl = URL.createObjectURL(audioBlob);
    clientLogger.debug("Playback URL created", {
      playbackUrl: this.playbackUrl,
    });
    return this.playbackUrl;
  };

  private cleanupData = () => {
    this.audioChunks = [];
  };

  private handleDataAvailable = (event: BlobEvent) => {
    clientLogger.debug("Data available", {
      data: event.data,
    });
    this.audioChunks.push(event.data);
  };

  private isRecording = () => {
    return this.mediaRecorder?.state === "recording";
  };
  // #endregion Recording Management

  // #region Audio Analysis
  private setupAudioAnalysis = () => {
    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    const source = this.audioContext.createMediaStreamSource(this.stream!);
    source.connect(this.analyser);

    // Monitor audio levels
    const checkAudioLevel = () => {
      if (!this.isRecording()) return;

      const dataArray = new Uint8Array(this.analyser!.frequencyBinCount);
      this.analyser!.getByteTimeDomainData(dataArray);

      // Check if we're getting any non-silence audio
      const isActive = dataArray.some((value) => Math.abs(value - 128) > 5);

      if (isActive !== this.isAudioActive) {
        this.isAudioActive = isActive;
        clientLogger.debug("Audio level check", {
          isActive,
          sampleValues: dataArray.slice(0, 10),
          timestamp: new Date().toISOString(),
        });
      }

      requestAnimationFrame(checkAudioLevel);
    };

    checkAudioLevel();
  };

  private stopTracks = () => {
    this.stream!.getTracks().forEach((track) => {
      track.stop();
      track.enabled = false;
    });
  };

  private cleanupAudioAnalysis = () => {
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.analyser = null;
  };
  // #endregion Audio Analysis

  // #region Transcription Management
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

  // #region Logging & Diagnostics
  private getBrowserInfo = () => {
    const userAgent = navigator.userAgent;
    const isFirefox = userAgent.includes("Firefox");
    const isChrome = userAgent.includes("Chrome");

    console.debug("Browser detection", {
      userAgent,
      isFirefox,
      isChrome,
      mimeType: this.mimeType,
    });

    return { isFirefox, isChrome };
  };
  // #endregion Logging & Diagnostics
}
