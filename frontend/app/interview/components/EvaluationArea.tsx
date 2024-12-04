import React from "react";
import { useWebsocketContext } from "../context/WebsocketContext";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

const renderEvaluation = (websocketFrames: WebsocketFrame[]) => {
  return websocketFrames
    .filter((websocketFrame) => websocketFrame.address === "thought")
    .map((websocketFrame) => {
      return (
        <div key={websocketFrame.frameId}>{websocketFrame.frame.content}</div>
      );
    });
};

const EvaluationArea = () => {
  const { state: frameList } = useWebsocketContext();
  return (
    <div className="flex flex-col gap-2 items-center md:w-1/3 w-full">
      {renderEvaluation(frameList.websocketFrames)}
    </div>
  );
};

export default EvaluationArea;
