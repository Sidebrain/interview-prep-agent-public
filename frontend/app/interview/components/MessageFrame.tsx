import { cn } from "@/lib/utils";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";
import Markdown from "react-markdown";

// const CompletionFrameChunkSchema = z.object({
//   id: z.string(),
//   object: z.enum([
//     "chat.completion",
//     "chat.completion.chunk",
//     "human.completion",
//   ]),
//   model: z.string(),
//   role: z.enum(["assistant", "user"]),
//   content: z.string().nullable(),
//   delta: z.string().nullable(),
//   createdTs: z.number().int().default(createTimestamp()), // unix timestamp
//   title: z.string().nullable(),
//   index: z.number(),
//   finishReason: z.enum([
//     "stop",
//     "length",
//     "tool_calls",
//     "content_filter",
//     "function_call",
//   ]),
// });

// const WebsocketFrameSchema = z.object({
//   // track changes: added "input" to type, added "human" to address
//   frameId: z.string(),
//   correlationId: z.string(),
//   type: z.enum([
//     "completion",
//     "streaming",
//     "heartbeat",
//     "error",
//     "input",
//     "signal.regenerate",
//   ]),
//   address: z.enum(["content", "artifact", "human", "thought"]).nullable(),
//   frame: CompletionFrameChunkSchema,
// });

// type WebsocketFrame = z.infer<typeof WebsocketFrameSchema>;

const MessageFrame = ({ frame }: { frame: WebsocketFrame }) => {
  return (
    <div
      className={cn(
        "flex flex-col border border-gray-300 rounded-md p-2 whitespace-pre-wrap",
        {
          "bg-black text-white": frame.frame.role === "user",
          "bg-white": frame.frame.role === "assistant",
        }
      )}
    >
      <Markdown>{frame.frame.content}</Markdown>
    </div>
  );
};

export default MessageFrame;
