type LogLevel = "debug" | "info" | "warn" | "error" | "off";

class Logger {
  private level: LogLevel;

  constructor(level: LogLevel = "info") {
    this.level = level;
  }

  setLevel(level: LogLevel) {
    this.level = level;
  }

  private getCallerLocation(): string {
    const error = new Error();
    const stack = error.stack;

    if (stack) {
      const stackLines = stack.split("\n");

      const callerStackLine = stackLines[3] || stackLines[4];

      if (callerStackLine) {
        console.debug("callerStackLine: ", callerStackLine);
        const match = callerStackLine.match(/\((.*):(\d+):(\d+)\)/);
        if (match) {
          const [, filePath, lineNum, colNum] = match;
          return `at ${filePath}:${lineNum}:${colNum}`;
        }
      }
    }

    return "at unknown location";
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = ["debug", "info", "warn", "error"];
    const currentLevelIndex = levels.indexOf(this.level);
    const requestedLevelIndex = levels.indexOf(level);

    return requestedLevelIndex >= currentLevelIndex && this.level !== "off";
  }

  debug(...args: any[]) {
    if (this.shouldLog("debug")) {
      console.debug("debug", ...args);
    }
  }

  info(...args: any[]) {
    if (this.shouldLog("info")) {
      console.info("info", ...args);
    }
  }

  warn(...args: any[]) {
    if (this.shouldLog("warn")) {
      console.warn("warn", ...args);
    }
  }

  error(...args: any[]) {
    if (this.shouldLog("error")) {
      console.error("error", ...args);
    }
  }
}

const serverLogger = new Logger(process.env.SERVER_LOG_LEVEL as LogLevel);
serverLogger.debug("server log level: ", process.env.SERVER_LOG_LEVEL);
export default serverLogger;
