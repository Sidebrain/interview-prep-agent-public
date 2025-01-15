import clientLogger from "@/app/lib/clientLogger";

export class StreamManager {
  private stream: MediaStream | null = null;

  constructor(private constraints: MediaStreamConstraints) {}

  public initialize = async () => {
    const mediaStream = await this.requestMediaStream();
    this.stream = mediaStream;
  };

  public isReady = () => this.stream !== null;

  public getStream = () => this.stream;

  public cleanup = async () => {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => {
        track.stop();
        track.enabled = false;
      });
      this.stream = null;
    }
  };

  private requestMediaStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(this.constraints);

      clientLogger.debug("Media permissions granted", {
        stream: stream,
      });

      return stream;
    } catch (error) {
      clientLogger.error("Failed to get media permissions", error);
      throw error;
    }
  };
}
