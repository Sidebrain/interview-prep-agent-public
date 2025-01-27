"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "./message-bubble";
import { useInterviewStore } from "@/lib/stores/interview-store";
import { ScrollArea } from "../ui/scroll-area";

export function MessageThread() {
  const messages = useInterviewStore((state) => state.messages);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <ScrollArea className="h-[calc(100vh-8rem)] pb-24 pr-80">
      <div ref={scrollRef} className="container max-w-3xl mx-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  );
}