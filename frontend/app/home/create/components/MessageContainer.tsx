"use client";
import clientLogger from "@/app/lib/clientLogger";
import { FrameType } from "@/reducers/messageFrameReducer";
import { useCallback, useEffect, useRef } from "react";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import Frame from "./Frame";

type MessageContainerProps = {
  setMaxTextareaHeight: (maxTextareaHeight: number) => void;
  frameList: FrameType[];
};

function MessageContainer(props: MessageContainerProps) {
  const containerAreaRef = useRef<HTMLDivElement>(null); // to calculate div height for textarea sizing

  // identify the max textarea height
  useEffect(() => {
    function computeMaxHeight() {
      if (containerAreaRef.current) {
        const containerHeight = containerAreaRef.current.clientHeight;
        const newMaxHeight = Math.max(50, Math.max(150, containerHeight * 0.7));
        clientLogger.debug("newMaxHeight: ", newMaxHeight);
        clientLogger.debug("containerHeight: ", containerHeight);
        props.setMaxTextareaHeight(newMaxHeight);
      }
    }
    computeMaxHeight();

    window.addEventListener("resize", computeMaxHeight);
    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);
  useEffect(() => {
    if (containerAreaRef.current) {
      containerAreaRef.current.scrollTop =
        containerAreaRef.current.scrollHeight;
    }
  }, [props.frameList]);
  return (
    <div
      ref={containerAreaRef}
      className="flex flex-col grow gap-2 overflow-auto text-sm no-scrollbar w-2/3 self-center "
    >
      {props.frameList.map((frame, idx) => (
        <Frame frame={frame} key={idx} />
      ))}
    </div>
  );
}

export default MessageContainer;
