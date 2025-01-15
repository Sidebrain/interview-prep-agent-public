import { useEffect, useRef } from "react";
import ConversationFrame from "./frames/ConversationFrame";
import clientLogger from "@/app/lib/clientLogger";
import { FrameList } from "../reducers/frameReducer";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import { frameRenderers } from "../services/frameRenderers";

type MessageContainerProps = FrameList & {
  setMaxTextareaHeight: (height: number) => void;
};

const MessageContainer = ({
  websocketFrames,
  setMaxTextareaHeight,
}: MessageContainerProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // identify the max textarea height
  useEffect(() => {
    const computeMaxHeight = () => {
      if (containerRef.current) {
        const containerHeight = containerRef.current.clientHeight;
        const newMaxHeight = Math.max(
          50,
          Math.max(150, containerHeight * 0.7)
        );
        setMaxTextareaHeight(newMaxHeight);

        clientLogger.debug({
          containerHeight,
          newMaxHeight,
        });
      }
    };
    computeMaxHeight();

    window.addEventListener("resize", computeMaxHeight);
    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);

  // scroll to bottom when new frames are added
  useEffect(() => {
    // add a small delay to ensure the DOM has updated
    const scrollTimeout = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTop =
          containerRef.current.scrollHeight;
      }
    }, 50);

    return () => clearTimeout(scrollTimeout);
  }, [websocketFrames]);

  return (
    <div
      ref={containerRef}
      className="flex flex-col grow gap-2 max-h-screen overflow-scroll text-sm no-scrollbar md:w-2/3 w-full items-start p-4 md:p-0"
    >
      {frameRenderers.conversation(websocketFrames)}
    </div>
  );
};

export default MessageContainer;
export type { MessageContainerProps };
