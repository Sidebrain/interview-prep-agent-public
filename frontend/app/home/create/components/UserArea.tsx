"use client";
import { useEffect, useRef, useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import useWebSocket from "@/hooks/useWebsocketNew";
import { Badge } from "@/components/ui/badge";

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

  const [isExpanded, setIsExpanded] = useState(false);

  const ExpandButton = () => {
    return (
      // <div className="flex w-full justify-center items-center">
      <Badge
        variant={"outline"}
        className="bg-gray-200 hover:bg-gray-100 cursor-pointer transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? "Hide Textarea" : "Show Textarea"}
      </Badge>
      // </div>
    );
  };
  return (
    <div className="flex flex-col gap-2 h-full">
      <Header />
      <MessageContainer
        setMaxTextareaHeight={setMaxTextareaHeight}
        frameList={frameList}
      />
      <ExpandButton />
      <InputArea
        maxTextareaHeight={maxTextareaHeight}
        isExpanded={isExpanded}
      />
    </div>
  );
}

export default UserArea;
