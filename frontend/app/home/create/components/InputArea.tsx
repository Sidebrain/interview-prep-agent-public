"use client";
import { useContext, useRef } from "react";
import TextareaResizable from "./TextAreaResizable";
import InputContext from "@/context/InputContext";
import { Button } from "@/components/ui/button";
import AudioButton from "./inputButtons/AudioButton";
import { useWebsocketContext } from "@/context/WebsocketContext";

type InputAreaProps = {
  maxTextareaHeight: number;
  isExpanded: boolean;
};

export default function InputArea(props: InputAreaProps) {
  const { sendMessage, frameHandler, createHumanInputFrame } =
    useWebsocketContext();
  const { state: inputValue, dispatch: dispatchInputValue } =
    useContext(InputContext);

  // refs
  const textareaRef = useRef<HTMLTextAreaElement>(null); // to access textarea element

  function handleSubmit(e: React.FormEvent) {
    if (!inputValue.trim()) {
      return;
    }
    e.preventDefault();
    const frameToSend = createHumanInputFrame(inputValue); // creates a frame with the input value
    frameHandler(frameToSend); // add to the message list
    sendMessage(frameToSend); // send to the server
    console.log("submitted value: ", inputValue);
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  }

  if (!props.isExpanded) {
    return null;
  }

  return (
    <div className="flex text-primary rounded-sm flex-col border border-gray-300 gap-2 items-end w-full ">
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
