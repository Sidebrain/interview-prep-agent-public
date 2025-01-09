"use client";
import React from "react";
import { WebsocketProvider } from "./context/WebsocketContext";
import { InputProvider } from "./context/InputContext";
import UserArea from "./components/UserArea";
import EvaluationArea from "./components/EvaluationArea";
import SuggestionArea from "./components/SuggestionArea";
import PerspectiveArea from "./components/PerspectiveArea";
import { useSearchParams } from "next/navigation";

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
        <div className="flex justify-center md:min-w-1/3 w-full m-2 gap-2">
          <EvaluationArea />
          <UserArea />
          <PerspectiveArea />
          {/* <SuggestionArea /> */}
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
