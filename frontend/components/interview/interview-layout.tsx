"use client";

import { MessageThread } from "./message-thread";
import { InputPanel } from "./input-panel";
import { Header } from "./header";
import { NotificationPanel } from "./notification-panel";

export function InterviewLayout() {
  return (
    <div className="flex flex-col h-screen bg-background">
      <Header />
      <main className="flex-1 overflow-hidden relative">
        <MessageThread />
        <NotificationPanel />
        <InputPanel />
      </main>
    </div>
  );
}