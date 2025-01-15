import clientLogger from "@/app/lib/clientLogger";

export class StreamManager {
  private stream: MediaStream | null = null;

  public initialize = async () => {
    const audioStream = await this.requestAudioStream();
    this.stream = audioStream;
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
}
