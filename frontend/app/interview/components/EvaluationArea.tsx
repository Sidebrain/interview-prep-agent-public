import React from "react";
import { useWebsocketContext } from "../context/WebsocketContext";
import { frameRenderers } from "../services/frameRenderers";

const EvaluationArea = () => {
  const { state: frameList } = useWebsocketContext();
  return (
    <div className="flex text-sm bg-green-100 relative p-2 flex-col gap-2 items-center md:w-1/3 w-full overflow-y-auto">
      <h2 className="text-lg font-bold sticky top-0 bg-green-400 w-full text-center rounded-md">
        Evaluation Area
      </h2>
      {frameRenderers.evaluation(frameList.websocketFrames)}
    </div>
  );
};

export default EvaluationArea;
