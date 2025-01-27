"use client";

import { MessageThread } from "./message-thread";
import { InputPanel } from "./input-panel";
import { Header } from "./header";
import { NotificationPanel } from "./notification-panel";
import { useWebsocketContext } from "@/app/shared/context/WebsocketContext";
import { useState } from "react";
import MessageContainer from "@/app/shared/components/MessageContainer";

export function InterviewLayout() {
  const { state: frameList } = useWebsocketContext();
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);
  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      <main className="flex-1 relative pt-8 mx-auto">
        <NotificationPanel
          websocketFrames={frameList.websocketFrames}
        />
        <div className="flex flex-col h-full">
          <MessageContainer
            websocketFrames={frameList.websocketFrames}
            setMaxTextareaHeight={setMaxTextareaHeight}
          />
          <InputPanel maxTextareaHeight={maxTextareaHeight} />
        </div>
      </main>
    </div>
  );
}
