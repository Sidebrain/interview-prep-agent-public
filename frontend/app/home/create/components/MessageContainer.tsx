"use client";
import clientLogger from "@/app/lib/clientLogger";
import { FrameType } from "@/reducers/messageFrameReducer";
import { useCallback, useEffect, useRef } from "react";
import Markdown, { Components, ExtraProps } from "react-markdown";
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import remarkGfm from "remark-gfm";
import javascript from "react-syntax-highlighter/dist/cjs/languages/prism/javascript";
import typescript from "react-syntax-highlighter/dist/cjs/languages/prism/typescript";
import python from "react-syntax-highlighter/dist/cjs/languages/prism/python";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";

SyntaxHighlighter.registerLanguage("javascript", javascript);
SyntaxHighlighter.registerLanguage("typescript", typescript);
SyntaxHighlighter.registerLanguage("python", python);

type MessageContainerProps = {
  setMaxTextareaHeight: (maxTextareaHeight: number) => void;
  frameList: FrameType[];
};

interface CodeProps {
  node?: any;
  inline?: any;
  className?: any;
  children?: any;
}

function MessageContainer(props: MessageContainerProps) {
  const containerAreaRef = useRef<HTMLDivElement>(null); // to calculate div height for textarea sizing

  // for rendering the frames
  const components: Components = {
    code: ({ node, inline, className, children, ...props }: CodeProps) => {
      const match = /language-(\w+)/.exec(className || "");
      return !inline && match ? (
        <SyntaxHighlighter
          {...props}
          PreTag={"div"}
          language={match[1]}
          style={oneDark}
        >
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      ) : (
        <code {...props} className={className}>
          {children}
        </code>
      );
    },
  };

  const renderContentFrame = useCallback(
    (frame: FrameType) =>
      frameRenderHandler({ frame: frame, address: "content" }),
    [props.frameList]
  );

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
      {props.frameList.map((frame) => renderContentFrame(frame))}
    </div>
  );
}

export default MessageContainer;
