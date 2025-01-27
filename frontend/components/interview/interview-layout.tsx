"use client";

import { MessageThread } from "./message-thread";
import { InputPanel } from "./input-panel";
import { Header } from "./header";
import { NotificationPanel } from "./notification-panel";
import { useWebsocketContext } from "@/app/shared/context/WebsocketContext";

export function InterviewLayout() {
  const { state: frameList } = useWebsocketContext();
  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      <main className="flex-1 overflow-hidden relative">
        <MessageThread websocketFrames={frameList.websocketFrames} />
        <NotificationPanel />
        <InputPanel />
      </main>
    </div>
  );
}