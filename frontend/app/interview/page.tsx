"use client";
import React from "react";
import { useWebSocket } from "./hooks/useWebSocket";
import { STATIC_STATUS_PAGES } from "next/dist/shared/lib/constants";

const InterviewPage = () => {
  const { state, dispatch, connectionStatus } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL_V3 || "",
    enabled: true,
  });
  return (
    <div>
      {connectionStatus}
      <div className="flex flex-col bg-red-200">
        {state.frames.map((frame, index) => (
          <div key={index}>{frame.frame.content}</div>
        ))}
      </div>
    </div>
  );
};

export default InterviewPage;
