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
    <div className="flex gap-2 items-end ">
      <TextareaResizable
        maxTextareaHeight={props.maxTextareaHeight}
        ref={textareaRef}
        handleSubmit={handleSubmit}
      />
      <Button onClick={handleSubmit}>Send</Button>
      <AudioButton />
    </div>
  );
}
