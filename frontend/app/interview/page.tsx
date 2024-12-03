"use client";
import React from "react";
import { WebsocketProvider } from "./context/WebsocketContext";
import { InputProvider } from "./context/InputContext";
import UserArea from "./components/UserArea";

const InterviewPage = () => {
  return (
    <WebsocketProvider
      options={{
        url: process.env.NEXT_PUBLIC_WS_URL_V3 || "",
        enabled: true,
      }}
    >
      <InputProvider>
        <div className="flex justify-center md:min-w-1/3 w-full m-2">
          <UserArea />
        </div>
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
