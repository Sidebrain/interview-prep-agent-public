export class HeartbeatHandler {
  private heartbeatTimer: NodeJS.Timeout | null = null;

  constructor(
    private readonly interval: number,
    private readonly sendMessage: (data: string) => void
  ) {}

  start(): void {
    this.stop();
    this.heartbeatTimer = setInterval(() => {
      this.sendMessage("ping");
    }, this.interval);
  }

  stop(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
}
