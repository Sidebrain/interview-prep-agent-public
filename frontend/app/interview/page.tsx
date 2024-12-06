"use client";
import React from "react";
import { WebsocketProvider } from "./context/WebsocketContext";
import { InputProvider } from "./context/InputContext";
import UserArea from "./components/UserArea";
import EvaluationArea from "./components/EvaluationArea";
import SuggestionArea from "./components/SuggestionArea";

const InterviewPage = () => {
  return (
    <WebsocketProvider
      options={{
        url: process.env.NEXT_PUBLIC_WS_URL_V3 || "",
        enabled: true,
      }}
    >
      <InputProvider>
        <div className="flex justify-center md:min-w-1/3 w-full m-2 gap-2">
          <EvaluationArea />
          <UserArea />
          <SuggestionArea />
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
