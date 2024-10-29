"use client";
import { useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import useWebSocket from "@/hooks/useWebsocketNew";
import { Badge } from "@/components/ui/badge";
import { PopoverComponent } from "./PopoverComponent";
import { HeaderSelect } from "./HeaderSelect";
import { FrameType } from "@/reducers/messageFrameReducer";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

function Header() {
  return (
    <header className="flex justify-center bg-gray-300 rounded-sm text-center p-2">
      <HeaderSelect />
    </header>
  );
}

type UserAreaProps = {
  frameList: FrameType[];
  sendMessage: (data: WebsocketFrame) => void;
  frameHandler: (frame: WebsocketFrame) => void;
};

function UserArea({ frameHandler, frameList, sendMessage }: UserAreaProps) {
  // this state is needed to pass the max height to the textarea
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);

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
    <div className="flex w-full flex-col gap-2 h-full">
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
        frameHandler={frameHandler}
      />
    </div>
  );
}

export default UserArea;
