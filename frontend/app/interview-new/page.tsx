"use client";

import { InterviewLayout } from "@/components/interview/interview-layout";
import { useSearchParams } from "next/navigation";
import { WebsocketProvider } from "../shared/context/WebsocketContext";
import { InputProvider } from "../shared/context/InputContext";

export default function Home() {
  const searchParams = useSearchParams();
  const interview_session_id = searchParams.get("interview_session_id");
  if (!interview_session_id) {
    return <div>No interview session id</div>;
  }

  return (
    <WebsocketProvider
      options={{
        url: process.env.NEXT_PUBLIC_WS_URL_V3 + "?interview_session_id=" + interview_session_id || "",
        enabled: true,
      }}
    >
      <InputProvider>
        <InterviewLayout />
      </InputProvider>
    </WebsocketProvider>
  );
}
