"use client";
import { useEffect, useRef, useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import useWebSocket from "@/hooks/useWebsocketNew";

function Header() {
  return (
    <header className="bg-gray-300 rounded-sm text-center">
      Options to learn/configure/etc
    </header>
  );
}

function UserArea() {
  // this state is needed to pass the max height to the textarea
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);
  const { frameList } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL_V2 as string,
  });

  return (
    <div className="flex flex-col gap-2 h-full">
      <Header />
      <MessageContainer
        setMaxTextareaHeight={setMaxTextareaHeight}
        frameList={frameList}
      />
      <InputArea maxTextareaHeight={maxTextareaHeight} />
    </div>
  );
}

export default UserArea;
