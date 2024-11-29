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
        <UserArea />
      </InputProvider>
    </WebsocketProvider>
  );
};

export default InterviewPage;
