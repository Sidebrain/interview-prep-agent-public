"use client";
import { useContext, useEffect, useRef, useState } from "react";
import TextareaResizable from "./TextAreaResizable";
import InputContext from "@/context/InputContext";
import { Button } from "@/components/ui/button";
import AudioButton from "./inputButtons/AudioButton";

type InputAreaProps = {
  maxTextareaHeight: number;
};

export default function InputArea(props: InputAreaProps) {
  const { state: inputValue, dispatch: dispatchInputValue } =
    useContext(InputContext);

  // refs
  const textareaRef = useRef<HTMLTextAreaElement>(null); // to access textarea element

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // send the value to the server
    console.log("submitted value: ", inputValue);
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  }

  return (
    <div className="flex bg-gray-50 rounded-sm flex-col border border-gray-300 gap-2 items-end w-full ">
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
