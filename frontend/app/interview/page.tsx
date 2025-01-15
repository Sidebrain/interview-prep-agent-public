"use client";
import React, { useEffect, useRef } from "react";
import { WebsocketProvider } from "../shared/context/WebsocketContext";
import { InputProvider } from "../shared/context/InputContext";
import UserArea from "../shared/components/UserArea";
import { useSearchParams } from "next/navigation";
import useVideo from "../shared/hooks/useVideo";
import Draggable from "react-draggable";

const VideoPlayer = () => {
  const videoElementRef = useRef<HTMLVideoElement>(null);
  const { isRecording, error, startStream, stopStream } = useVideo({ videoElementRef });

  useEffect(() => {
    startStream();
    return () => {
      stopStream();
    };
  }, [startStream, stopStream]);

  return (
    <Draggable bounds="parent" handle=".handle">
      <div className="absolute cursor-move">
        <div className="handle bg-gray-800 p-1 text-xs text-gray-400 text-center">Drag here</div>
        <video className="w-32 h-32" ref={videoElementRef} autoPlay playsInline />
      </div>
    </Draggable>
  );
};

const InterviewPage = () => {
  const searchParams = useSearchParams();
  const interview_session_id = searchParams.get("interview_session_id");
  
  return (
    <WebsocketProvider
      options={{
        url: process.env.NEXT_PUBLIC_WS_URL_V3 + "?interview_session_id=" + interview_session_id || "",
        enabled: true,
      }}
    >
      <InputProvider>
        <div className="relative flex justify-center md:min-w-1/3 w-full h-screen m-2 gap-2">
          <VideoPlayer />
          <UserArea />
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
