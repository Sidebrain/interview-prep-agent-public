import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const PerspectiveFrame = ({
  websocketFrame,
}: {
  websocketFrame: WebsocketFrame;
}) => {
  return (
    <div className="border border-blue-300 rounded-lg p-4 m-2 bg-blue-50 shadow-sm hover:shadow-md transition-shadow duration-200 max-w-3xl">
      <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
        <Markdown
          className="markdown-content break-words text-sm"
          remarkPlugins={[remarkGfm]}
        >
          {websocketFrame.frame.content}
        </Markdown>
      </div>
    </div>
  );
};

export default PerspectiveFrame;
