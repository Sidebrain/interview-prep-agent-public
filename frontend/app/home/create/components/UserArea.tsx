"use client";
import { useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import { Badge } from "@/components/ui/badge";
import { FrameType } from "@/reducers/messageFrameReducer";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

function Header() {
  return (
    <header className="flex justify-center bg-gray-300 rounded-sm text-center p-0 font-bold text-gray-600">
      Interview Assistant
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

  const [isExpanded, setIsExpanded] = useState(true);

  const ExpandButton = () => {
    return (
      <div className="flex w-full items-center">
        <Badge
          variant={"outline"}
          className="bg-gray-200 hover:bg-gray-100 cursor-pointer transition-colors w-full p-1"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? "Hide Textarea" : "Show Textarea"}
        </Badge>
      </div>
    );
  };
  return (
    <div className="flex w-full flex-col gap-2 h-full pr-2">
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
