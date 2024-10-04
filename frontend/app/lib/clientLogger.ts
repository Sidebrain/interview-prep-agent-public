"use client";

type LogLevel = "debug" | "info" | "warn" | "error" | "off";

class ClientLogger {
  private level: LogLevel;

  constructor(level: LogLevel = "info") {
    this.level = level;
  }

  setLevel(level: LogLevel) {
    this.level = level;
  }

  debug(...args: any[]) {
    if (this.shouldLog("debug")) {
      console.debug("[DEBUG]:", ...args);
    }
  }

  info(...args: any[]) {
    if (this.shouldLog("info")) {
      console.info("[INFO]:", ...args);
    }
  }

  warn(...args: any[]) {
    if (this.shouldLog("warn")) {
      console.warn("[WARN]:", ...args);
    }
  }

  error(...args: any[]) {
    if (this.shouldLog("error")) {
      console.error("[ERROR]:", ...args);
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = ["debug", "info", "warn", "error"];
    const currentLevelIndex = levels.indexOf(this.level);
    const requestedLevelIndex = levels.indexOf(level);
    return requestedLevelIndex >= currentLevelIndex && this.level !== "off";
  }
}

const clientLogger = new ClientLogger(
  process.env.NEXT_PUBLIC_CLIENT_LOG_LEVEL as LogLevel
);
console.log("log level: ", process.env.NEXT_PUBLIC_CLIENT_LOG_LEVEL);
export default clientLogger;
