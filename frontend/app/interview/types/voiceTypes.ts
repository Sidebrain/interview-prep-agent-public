type VoiceHookParams = {
  chunkSize?: number;
  maxRecordingTime?: number;
  onTranscription?: (transcription: string) => void;
};

export type { VoiceHookParams };