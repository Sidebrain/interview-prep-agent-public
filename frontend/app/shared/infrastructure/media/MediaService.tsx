import { StreamManager } from "./StreamManager";
import { MediaStreamRecorder } from "./MediaStreamRecorder";
import { MediaProcessor, MediaProcessorMap, MediaServiceConfig, MediaServiceInterface } from "./types";


export class MediaService implements MediaServiceInterface {
  private streamManager: StreamManager;
  private recorder: MediaStreamRecorder;
  private processors: MediaProcessorMap;

  constructor({ 
    mimeType = "audio/webm", 
    constraints = {audio: true}, 
    timeslice, 
    processors = {}
  }: MediaServiceConfig) {
    this.streamManager = new StreamManager(constraints);
    this.recorder = new MediaStreamRecorder(mimeType, timeslice);
    this.processors = processors;
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

  public runAllProcessors = async (media: Blob | null) => {
    for (const processor of Object.values(this.processors)) {
      const result = await processor.process(media);
      if (result) {
        return result;
      }
    }
    return null;
  };

  public runProcessor = async (media: Blob | null, processorType: keyof MediaProcessorMap) => {
    const processor = this.processors[processorType];
    if (!processor) {
      throw new Error(`Processor ${processorType} not found`);
    }
    const result = await processor.process(media);
    if (result) {
      return result;
    }
    return null;
  };

  public cleanup = async () => {
    await this.streamManager.cleanup();
    await this.recorder.cleanup();
  };
}
