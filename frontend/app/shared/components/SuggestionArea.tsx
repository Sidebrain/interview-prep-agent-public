import { frameRenderers } from "../services/frameRenderers";
import { useWebsocketContext } from "../context/WebsocketContext";

const SuggestionArea = () => {
  const { state: frameList } = useWebsocketContext();
  const suggestion = frameRenderers.currentSuggestion(
    frameList.websocketFrames
  );
  return (
    <div className="flex bg-blue-100 relative p-2 flex-col gap-2 items-center md:w-1/3 w-full overflow-y-auto">
      <h2 className="text-lg font-bold sticky top-0 bg-blue-400 w-full text-center rounded-md">
        Suggestion
      </h2>
      <div className="flex h-full items-center">{suggestion}</div>
    </div>
  );
};

export default SuggestionArea;
