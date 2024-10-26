"use client";
import { useContext, useEffect, useRef, useState } from "react";
import TextareaResizable from "./TextAreaResizable";
import InputContext from "@/context/InputContext";
import { Button } from "@/components/ui/button";
import AudioButton from "./inputButtons/AudioButton";
import { send } from "process";
import { WebsocketSendTypes } from "@/types/WebsocketSendTypes";

type InputAreaProps = {
  maxTextareaHeight: number;
  isExpanded: boolean;
  sendMessage: (data: WebsocketSendTypes) => void;
};

// Badge,
// popopver is a nice place to bundle options ttogether
// Scroll area for improving the default scrolling behaviour
//

export default function InputArea(props: InputAreaProps) {
  const { state: inputValue, dispatch: dispatchInputValue } =
    useContext(InputContext);

  // refs
  const textareaRef = useRef<HTMLTextAreaElement>(null); // to access textarea element

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // send the value to the server
    props.sendMessage({ userInput: inputValue } as WebsocketSendTypes);
    console.log("submitted value: ", inputValue);
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  }

  if (!props.isExpanded) {
    return null;
  }

  return (
    <div className="flex text-white bg-gray-500 rounded-sm flex-col border border-gray-300 gap-2 items-end w-full ">
      <TextareaResizable
        maxTextareaHeight={props.maxTextareaHeight}
        ref={textareaRef}
        handleSubmit={handleSubmit}
      />
      <div
        className="flex bg-gray-100 border-t border-gray-200 rounded-b-sm
       justify-between items-center w-full p-1"
      >
        <AudioButton />
        <Button onClick={handleSubmit} size={"sm"}>
          Send
        </Button>
      </div>
    </div>
  );
}
