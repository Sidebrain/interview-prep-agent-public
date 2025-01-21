"use client";
import React from "react";
import { WebsocketProvider } from "../shared/context/WebsocketContext";
import { InputProvider } from "../shared/context/InputContext";
import UserArea from "../shared/components/UserArea";
import EvaluationArea from "../shared/components/EvaluationArea";
import SuggestionArea from "../shared/components/SuggestionArea";
import PerspectiveArea from "../shared/components/PerspectiveArea";
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
          <SuggestionArea />
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
