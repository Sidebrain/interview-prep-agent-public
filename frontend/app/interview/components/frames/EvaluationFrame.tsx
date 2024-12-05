import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

const EvaluationFrame = ({
  websocketFrame,
}: {
  websocketFrame: WebsocketFrame;
}) => {
  return (
    <div>
      <div
        className="border border-gray-300 rounded-md p-2 whitespace-pre-wrap m-1"
        key={websocketFrame.frameId}
      >
        {websocketFrame.frame.content}
      </div>
    </div>
  );
};

export default EvaluationFrame;
