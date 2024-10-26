import { z } from "zod";

// zod types for type validation

const CompletionFrameChunkSchema = z.object({
  id: z.string(),
  object: z.enum(["chat.completion", "chat.completion.chunk"]),
  model: z.string(),
  role: z.literal("assistant"),
  content: z.string().nullable(),
  delta: z.string().nullable(),
  index: z.number(),
  finishReason: z.enum([
    "stop",
    "length",
    "tool_calls",
    "content_filter",
    "function_call",
  ]),
});

type CompletionFrameChunk = z.infer<typeof CompletionFrameChunkSchema>;

const WebsocketFrameSchema = z.object({
  frameId: z.string(),
  type: z.enum(["completion", "streaming", "heartbeat", "error"]),
  address: z.enum(["content", "artefact"]).nullable(),
  frame: CompletionFrameChunkSchema,
});

type WebsocketFrame = z.infer<typeof WebsocketFrameSchema>;

export type {
  // types received from websocket
  CompletionFrameChunk,
  WebsocketFrame,
};

// zod types for type validation on the websocket
export { CompletionFrameChunkSchema, WebsocketFrameSchema };
