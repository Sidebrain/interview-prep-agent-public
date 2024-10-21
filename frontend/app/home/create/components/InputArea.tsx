"use client";
import { useContext, useEffect, useRef, useState } from "react";
import TextareaResizable from "./TextAreaResizable";
import InputContext from "@/context/InputContext";

type InputAreaProps = {
  //
};

export default function InputArea(props: InputAreaProps) {
  const { state: inputValue, dispatch: dispatchInputValue } =
    useContext(InputContext);

  // refs
  const inputAreaRef = useRef<HTMLDivElement>(null); // to calculate div height for textarea sizing
  const textareaRef = useRef<HTMLTextAreaElement>(null); // to access textarea element
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(50);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // send the value to the server
    console.log("submitted value: ", inputValue);
    dispatchInputValue({ type: "SET_INPUT", payload: "" });
  }

  // identify the max textarea height
  useEffect(() => {
    function computeMaxHeight() {
      if (inputAreaRef.current) {
        const containerHeight = inputAreaRef.current.clientHeight;
        const newMaxHeight = Math.min(50, Math.max(150, containerHeight * 0.7));
        setMaxTextareaHeight(newMaxHeight);
      }
    }

    window.addEventListener("resize", computeMaxHeight);
    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);
  return (
    <TextareaResizable
      maxTextareaHeight={maxTextareaHeight}
      ref={textareaRef}
      handleSubmit={handleSubmit}
    />
  );
}
