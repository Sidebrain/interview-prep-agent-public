"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "./message-bubble";
import { useInterviewStore } from "@/lib/stores/interview-store";
import { ScrollArea } from "../ui/scroll-area";
import { FrameList } from "@/app/shared/reducers/frameReducer";
import { frameRenderers } from "@/app/shared/services/frameRenderers";

type MessageContainerProps = FrameList & {
};

export function MessageThread({ websocketFrames }: MessageContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [websocketFrames]);

  return (
    <ScrollArea className="h-[calc(100vh-8rem)] pb-24 pr-80">
      <div ref={scrollRef} className="container max-w-3xl mx-auto p-4 space-y-4">
        {frameRenderers.messageBubble(websocketFrames)}
      </div>
    </ScrollArea>
  );
}