import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import React from "react";
import { tryParseJSON } from "@/app/lib/helperFunctions";
import { RecursiveEvaluationFrame } from "./RecursiveEvaluationFrame";

const EvaluationFrame = ({
  websocketFrame,
}: {
  websocketFrame: WebsocketFrame;
}) => {
  const content = websocketFrame.frame.content;
  if (content === null) {
    return null;
  }

  const structuredContent = tryParseJSON(content);
  if (structuredContent === null) {
    return (
      <div className="border w-full border-gray-300 rounded-md p-2 m-1 whitespace-pre-wrap">
        {content}
      </div>
    );
  }

  return (
    <div>
      <div
        className="border border-gray-300 rounded-md p-2 whitespace-pre-wrap m-1 "
        key={websocketFrame.frameId}
      >
        <RecursiveEvaluationFrame data={structuredContent} />
      </div>
    </div>
  );
};

export default EvaluationFrame;
