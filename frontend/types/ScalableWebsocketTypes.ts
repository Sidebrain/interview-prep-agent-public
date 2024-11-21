import { z } from "zod";
import { createTimestamp } from "@/app/lib/helperFunctions";

// zod types for type validation

const CompletionFrameChunkSchema = z.object({
  id: z.string(),
  object: z.enum([
    "chat.completion",
    "chat.completion.chunk",
    "human.completion",
  ]),
  model: z.string(),
  role: z.enum(["assistant", "user"]),
  content: z.string().nullable(),
  delta: z.string().nullable(),
  createdTs: z.number().int().default(createTimestamp()), // unix timestamp
  title: z.string().nullable(),
  index: z.number(),
  finishReason: z.enum([
    "stop",
    "length",
    "tool_calls",
    "content_filter",
    "function_call",
  ]),
});

const ThoughtSchema = z.object({
  question: z.string(),
  sampleAnswer: z.string(),
  options: z.string(),
});

export type Thought = z.infer<typeof ThoughtSchema>;

type CompletionFrameChunk = z.infer<typeof CompletionFrameChunkSchema>;

const WebsocketFrameSchema = z.object({
  // track changes: added "input" to type, added "human" to address
  frameId: z.string(),
  type: z.enum([
    "completion",
    "streaming",
    "heartbeat",
    "error",
    "input",
    "signal.regenerate",
  ]),
  address: z.enum(["content", "artifact", "human", "thought"]).nullable(),
  frame: CompletionFrameChunkSchema,
});

type WebsocketFrame = z.infer<typeof WebsocketFrameSchema>;

export type {
  // types received from websocket
  CompletionFrameChunk,
  WebsocketFrame,
};

// zod types for type validation on the websocket
export { CompletionFrameChunkSchema, WebsocketFrameSchema, ThoughtSchema };
