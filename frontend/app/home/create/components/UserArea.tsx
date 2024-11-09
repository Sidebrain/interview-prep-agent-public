"use client";
import { useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";
import { Badge } from "@/components/ui/badge";
import HelperContent from "./HelperContent";
import { useArtifact } from "@/context/ArtifactContext";
import { useWebsocketContext } from "@/context/WebsocketContext";

function Header() {
  return (
    <header className="flex justify-center bg-gray-300 rounded-sm text-center p-0 font-bold text-gray-600">
      Interview Assistant
    </header>
  );
}

type UserAreaProps = {};

function UserArea({}: UserAreaProps) {
  // this state is needed to pass the max height to the textarea
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);
  const { frameList } = useWebsocketContext();
  const { artifacts } = useArtifact();

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
    <div
      className={`flex ${
        artifacts ? "hidden md:flex md:w-1/2" : "w-full md:w-1/2"
      } flex-col gap-2 h-full pr-2`}
    >
      <Header />
      <MessageContainer
        setMaxTextareaHeight={setMaxTextareaHeight}
        frameList={frameList}
      />
      {frameList.length > 0 && (
        <HelperContent frame={frameList[frameList.length - 1]} />
      )}
      <ExpandButton />
      <InputArea
        maxTextareaHeight={maxTextareaHeight}
        isExpanded={isExpanded}
      />
    </div>
  );
}

export default UserArea;
