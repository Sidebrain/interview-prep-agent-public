"use client";
import clientLogger from "@/app/lib/clientLogger";
import { FrameType } from "@/types/reducerTypes";
import { useEffect, useRef } from "react";
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
    // Add a small delay to ensure the DOM has updated
    const scrollTimeout = setTimeout(() => {
      if (containerAreaRef.current) {
        containerAreaRef.current.scrollTop = containerAreaRef.current.scrollHeight;
      }
    }, 0);

    return () => clearTimeout(scrollTimeout);
  }, [props.frameList.length, props.frameList.map(frame => frame.frame?.content)]);

  return (
    <div
      ref={containerAreaRef}
      className="flex flex-col grow gap-2 overflow-auto text-sm no-scrollbar md:w-2/3 w-full self-center p-4 md:p-0"
    >
      {/* {props.frameList.map((frame) => renderContentFrame(frame))} */}
      {props.frameList.map((frame, idx) => (
        <Frame frame={frame} key={idx} />
      ))}
    </div>
  );
}

export default MessageContainer;
