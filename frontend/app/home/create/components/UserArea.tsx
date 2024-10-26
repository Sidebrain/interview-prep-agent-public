"use client";
import { useEffect, useRef, useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import useWebSocket from "@/hooks/useWebsocketNew";
import { Badge } from "@/components/ui/badge";
import { PopoverComponent } from "./PopoverComponent";
import { HeaderSelect } from "./HeaderSelect";

function Header() {
  return (
    <header className="flex justify-center bg-gray-300 rounded-sm text-center p-2">
      <HeaderSelect />
    </header>
  );
}

function UserArea() {
  // this state is needed to pass the max height to the textarea
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);
  const { frameList, sendMessage } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL_V2 as string,
  });

  const [isExpanded, setIsExpanded] = useState(false);

  const ExpandButton = () => {
    return (
      <div className="flex w-full items-center gap-2">
        <Badge
          variant={"outline"}
          className="bg-gray-200 hover:bg-gray-100 cursor-pointer transition-colors w-full p-1"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? "Hide Textarea" : "Show Textarea"}
        </Badge>
        <PopoverComponent />
      </div>
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
        sendMessage={sendMessage}
      />
    </div>
  );
}

export default UserArea;
