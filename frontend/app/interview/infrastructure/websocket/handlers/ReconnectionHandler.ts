import clientLogger from "@/app/lib/clientLogger";

export class ReconnectHandler {
  private reconnectCount: number = 0;
  constructor(
    private readonly maxAttempts: number,
    private readonly interval: number,
    private readonly onReconnect: () => void
  ) {}
  handleReconnect(): void {
    if (this.reconnectCount < this.maxAttempts) {
      setTimeout(() => {
        this.reconnectCount++;

        clientLogger.debug("Reconnecting to WebSocket", {
          reconnectCount: this.reconnectCount,
        });

        this.onReconnect();
      }, this.interval);
    }
  }

  reset(): void {
    this.reconnectCount = 0;
  }
}
