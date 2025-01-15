import { tryParseJSON } from "@/app/lib/helperFunctions";
import { cn } from "@/lib/utils";
import { ThoughtSchema, WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import Markdown from "react-markdown";

const ConversationFrame = ({
  websocketFrame,
}: {
  websocketFrame: WebsocketFrame;
}) => {
  let content = websocketFrame.frame.content;
  const structuredContent = tryParseJSON(content);

  if (structuredContent !== null) {
    // try parsing for a thought
    const { success, data } = ThoughtSchema.safeParse(structuredContent);
    if (success) {
      content = data.question;
    }
  }

  return (
    <div
      className={cn(
        "flex flex-col border border-gray-300 rounded-md p-2 whitespace-pre-wrap",
        {
          "bg-black text-white": websocketFrame.frame.role === "user",
          "bg-white": websocketFrame.frame.role === "assistant",
        }
      )}
    >
      <Markdown>{content}</Markdown>
    </div>
  );
};

export default ConversationFrame;
