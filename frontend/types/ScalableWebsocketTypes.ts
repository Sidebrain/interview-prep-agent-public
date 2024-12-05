import { z } from "zod";
import { createTimestamp } from "@/app/lib/helperFunctions";

// Centralized enums
const ObjectType = [
  "chat.completion",
  "chat.completion.chunk",
  "human.completion",
] as const;
const RoleType = ["assistant", "user"] as const;
const FinishReasonType = [
  "stop",
  "length",
  "tool_calls",
  "content_filter",
  "function_call",
] as const;
const FrameType = [
  "completion",
  "streaming",
  "heartbeat",
  "error",
  "input",
  "signal.regenerate",
] as const;
const AddressType = [
  "content",
  "artifact",
  "human",
  "thought",
  "evaluation",
] as const;

// zod types for type validation

const CompletionFrameChunkSchema = z.object({
  id: z.string(),
  object: z.enum(ObjectType),
  model: z.string(),
  role: z.enum(RoleType),
  content: z.string().nullable(),
  delta: z.string().nullable(),
  createdTs: z.number().int().default(createTimestamp()), // unix timestamp
  title: z.string().nullable(),
  index: z.number(),
  finishReason: z.enum(FinishReasonType),
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
  correlationId: z.string(),
  type: z.enum(FrameType),
  address: z.enum(AddressType).nullable(),
  frame: CompletionFrameChunkSchema,
});

type WebsocketFrame = z.infer<typeof WebsocketFrameSchema>;

export type {
  // types received from websocket
  CompletionFrameChunk,
  WebsocketFrame,
};

// zod types for type validation on the websocket
export {
  CompletionFrameChunkSchema,
  WebsocketFrameSchema,
  ThoughtSchema,
};

export type {
  AddressType,
  FrameType,
  ObjectType,
  RoleType,
  FinishReasonType,
};
