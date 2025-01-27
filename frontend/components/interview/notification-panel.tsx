"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Clock, Mic, AlertTriangle, BarChart } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import { ScrollArea } from "../ui/scroll-area";
import { Progress } from "../ui/progress";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { frameRenderers } from "@/app/shared/services/frameRenderers";
import { FrameList } from "@/app/shared/reducers/frameReducer";

// Helper functions
function getNotificationIcon(type: WebsocketFrame["frame"]["notificationType"]) {
  switch (type) {
    case "word-usage":
      return BarChart;
    case "time":
      return Clock;
    case "performance":
      return Mic;
    case "technical":
      return AlertTriangle;
    default:
      return AlertTriangle;
  }
}

function getSeverityColor(severity: WebsocketFrame["frame"]["severity"]) {
  switch (severity) {
    case "error":
      return "text-destructive";
    case "warning":
      return "text-yellow-500";
    case "info":
    default:
      return "text-blue-500";
  }
}

// Sub-components
interface NotificationHeaderProps {
  progress: number;
}

function NotificationHeader({ progress }: NotificationHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-semibold">Feedback</h2>
      <div className="flex items-center gap-2">
        <Progress value={progress} className="w-20" />
        <span className="text-sm text-muted-foreground">{progress}%</span>
      </div>
    </div>
  );
}

export function NotificationItem({ notification }: { notification: WebsocketFrame }) {
  // Ensure the notification object exists and has the expected structure
  if (!notification?.frame) {
    return null; // Or some fallback UI
  }

  const Icon = getNotificationIcon(notification.frame.notificationType);

  return (
    <div className="p-3 bg-muted rounded-lg animate-in slide-in-from-right">
      <div className="flex items-start gap-3">
        <Icon className={cn("h-5 w-5", getSeverityColor(notification.frame.severity))} />
        <div className="flex-1 min-w-0">
          <p className="text-sm">{notification.frame.content}</p>
          <time className="text-xs text-muted-foreground">
            {new Intl.DateTimeFormat("en", {
              hour: "numeric",
              minute: "numeric",
            }).format(new Date(notification.frame.createdTs * 1000))}
          </time>
        </div>
      </div>
    </div>
  );
}

function NotificationList({ websocketFrames }: FrameList) {
  return (
    <ScrollArea className="flex-1">
      <div className="space-y-4">
      {frameRenderers.notification(websocketFrames)}
      </div>
    </ScrollArea>
  );
}

// Main component
export function NotificationPanel({websocketFrames}: FrameList ) {
  const [isExpanded, setIsExpanded] = useState(true);
  return (
    <div
      className={cn(
        "fixed right-0 top-14 h-[calc(100vh-3.5rem)] bg-card border-l transition-all duration-300 ease-in-out",
        isExpanded ? "w-80" : "w-12"
      )}
    >
      <Button
        variant="ghost"
        size="icon"
        className="absolute -left-10 top-4"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? <ChevronRight /> : <ChevronLeft />}
      </Button>

      {isExpanded && (
        <div className="p-4 h-full flex flex-col">
          <NotificationHeader progress={75} />
          <NotificationList websocketFrames={websocketFrames} />
        </div>
      )}
    </div>
  );
}