"use client";
import React, { useEffect, useRef } from "react";
import { WebsocketProvider } from "../shared/context/WebsocketContext";
import { InputProvider } from "../shared/context/InputContext";
import UserArea from "../shared/components/UserArea";
import { useSearchParams } from "next/navigation";
import useVideo from "../shared/hooks/useVideo";
import Draggable from "react-draggable";
import { Button } from "@/components/ui/button";

const VideoPlayer = ({ interview_session_id }: { interview_session_id: string }) => {
  const videoElementRef = useRef<HTMLVideoElement>(null);
  const { isRecording, error, startStream, stopStream, uploadVideo, startRecording, stopRecording } = useVideo({ 
    videoElementRef, 
    interview_session_id 
  });

  useEffect(() => {

    const initStream = async () => {
      await startStream();
    };

    initStream();

    return () => {
      stopStream();
    };
  }, []);

  const handleUpload = async () => {
    if (isRecording) {
      await stopRecording();
    }
    await uploadVideo();
  };

  return (
    <Draggable bounds="parent" handle=".handle">
      <div className="absolute cursor-move">
        <div className="handle bg-gray-800 p-1 text-xs text-gray-400 text-center">Drag here</div>
        <video className="w-64 h-32" ref={videoElementRef} autoPlay playsInline muted />
        <Button onClick={startRecording}>Start Recording</Button>
        <Button onClick={stopRecording}>Stop Recording</Button>
        <Button onClick={handleUpload}>Upload</Button>
      </div>
    </Draggable>
  );
};

const InterviewPage = () => {
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
        <div className="relative flex justify-center md:min-w-1/3 w-full h-screen m-2 gap-2">
          <VideoPlayer interview_session_id={interview_session_id} />
          <UserArea />
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
