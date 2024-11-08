import { FrameType } from "@/types/reducerTypes";
import Markdown, { Components } from "react-markdown";
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import remarkGfm from "remark-gfm";
import javascript from "react-syntax-highlighter/dist/cjs/languages/prism/javascript";
import typescript from "react-syntax-highlighter/dist/cjs/languages/prism/typescript";
import python from "react-syntax-highlighter/dist/cjs/languages/prism/python";
import json from "react-syntax-highlighter/dist/cjs/languages/prism/json";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

SyntaxHighlighter.registerLanguage("javascript", javascript);
SyntaxHighlighter.registerLanguage("typescript", typescript);
SyntaxHighlighter.registerLanguage("python", python);
SyntaxHighlighter.registerLanguage("json", json);

interface CodeProps {
  node?: any;
  inline?: any;
  className?: any;
  children?: any;
}

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

type RenderFrameType = {
  frame: FrameType;
  address: WebsocketFrame["address"];
};

export const frameRenderHandler = ({ frame, address }: RenderFrameType) => {
  switch (address) {
    case "thought":
      return (
        <>
          {frame.thoughtFrames.map((tframe, idx) => (
            <div className="border border-gray-400 p-2 m-2" key={idx}>
              {/* <SyntaxHighlighter
                language="json"
                style={oneDark}
                PreTag={"div"}
                remarkPlugins={[remarkGfm]}
                components={components}
                className="markdown-content break-words text-sm"
                wrapLines={true}
                wrapLongLines={true}
                key={`tframe-${idx}`}
              > */}
              {`${tframe.content}`}
              {/* </SyntaxHighlighter> */}
            </div>
          ))}
        </>
      );
    case "artifact":
      return (
        <div className="flex flex-col gap-2">
          {frame.artifactFrames.map((aframe, idx) => (
            <div className="border border-gray-400 p-2 m-2" key={idx}>
              <Markdown
                remarkPlugins={[remarkGfm]}
                components={components}
                className="markdown-content break-words text-sm "
                key={`artifact-${idx}`}
              >
                {aframe.content}
              </Markdown>
            </div>
          ))}
        </div>
      );
    case "content":
    default:
      return (
        <div
          className={`mb-4 ${
            frame.contentFrame.role === "user" ? "text-left" : "text-left"
          }`}
        >
          <span
            className={`inline-block p-2 rounded-lg max-w-full ${
              frame.contentFrame.role === "user"
                ? "bg-gray-100 text-gray-800 border border-gray-200"
                : "bg-gray-300 text-black"
            }`}
          >
            <Markdown
              remarkPlugins={[remarkGfm]}
              components={components}
              className="markdown-content break-words "
            >
              {frame.contentFrame.content?.trim()}
            </Markdown>
          </span>
        </div>
      );
  }
};
