import { z } from "zod";
import { createTimestamp } from "@/app/lib/helperFunctions";

// Centralized enums

// Centralized enums
export const ObjectType = [
  "chat.completion",
  "chat.completion.chunk",
  "human.completion",
] as const;

export const RoleType = ["assistant", "user"] as const;

export const FinishReasonType = [
  "stop",
  "length",
  "tool_calls",
  "content_filter",
  "function_call",
] as const;

export const FrameType = [
  "completion",
  "streaming",
  "heartbeat",
  "error",
  "input",
  "signal.regenerate",
] as const;

export const AddressType = [
  "content",
  "artifact",
  "human",
  "thought",
  "evaluation",
  "perspective",
] as const;

// Convert the arrays to Zod enums
export const MediaTypeEnum = z.enum(["image", "video", "audio", "code", "file", "link"]);
export const NotificationTypeEnum = z.enum(["word-usage", "time", "performance", "technical"]).default("word-usage");
export const SeverityEnum = z.enum(["info", "warning", "error"]).default("info");

// Media-related schemas
export const MediaContentSchema = z.object({
  type: MediaTypeEnum,
  url: z.string().optional(),
  title: z.string().optional(),
  mimeType: z.string().optional(),
  language: z.string().optional(),
  code: z.string().optional(),
  thumbnail: z.string().optional(),
  duration: z.number().optional(),
  size: z.number().optional(),
  width: z.number().optional(),
  height: z.number().optional(),
  aspectRatio: z.number().optional(),
  previewUrl: z.string().optional(),
});

// Completion frame chunk schema
export const CompletionFrameChunkSchema = z.object({
  id: z.string(),
  object: z.enum(ObjectType),
  model: z.string(),
  role: z.enum(RoleType),
  content: z.string().nullable(),
  delta: z.string().nullable(),
  createdTs: z.number().int().default(createTimestamp()),
  title: z.string().nullable(),
  index: z.number(),
  finishReason: z.enum(FinishReasonType),
  media: z.array(MediaContentSchema).optional(),
  notificationType: NotificationTypeEnum.optional(),
  severity: SeverityEnum.optional(),
});

// Thought schema
export const ThoughtSchema = z.object({
  question: z.string(),
  sampleAnswer: z.string(),
  options: z.string(),
});

// Websocket frame schema (main message type)
export const WebsocketFrameSchema = z.object({
  frameId: z.string(),
  correlationId: z.string(),
  type: z.enum(FrameType),
  address: z.enum(AddressType).nullable(),
  frame: CompletionFrameChunkSchema,
  loading: z.boolean().optional(),
});

// Type exports
export type MediaType = z.infer<typeof MediaTypeEnum>;
export type MediaContent = z.infer<typeof MediaContentSchema>;
export type WebsocketFrameType = z.infer<typeof WebsocketFrameSchema>;
export type Thought = z.infer<typeof ThoughtSchema>;
export type CompletionFrameChunk = z.infer<typeof CompletionFrameChunkSchema>;
export type NotificationType = z.infer<typeof NotificationTypeEnum>;
export type Severity = z.infer<typeof SeverityEnum>;

// Helper function to create a new message
export const createMessage = (data: Partial<CompletionFrameChunk>): WebsocketFrameType => {
  const frameId = crypto.randomUUID();
  return WebsocketFrameSchema.parse({
    frameId,
    correlationId: data.id ?? frameId,
    type: "completion",
    address: "content",
    frame: CompletionFrameChunkSchema.parse({
      id: data.id ?? frameId,
      object: data.object ?? "chat.completion",
      model: data.model ?? "gpt-4",
      role: data.role ?? "user",
      content: data.content ?? null,
      delta: data.delta ?? null,
      createdTs: data.createdTs ?? createTimestamp(),
      title: data.title ?? null,
      index: data.index ?? 0,
      finishReason: data.finishReason ?? "stop",
      media: data.media,
      notificationType: data.notificationType,
      severity: data.severity,
    }),
    loading: false,
  });
};

// Helper function to create a new notification
export const createNotification = (
  type: NotificationType,
  content: string,
  severity: Severity = "info"
): WebsocketFrameType => {
  const frameId = crypto.randomUUID();
  return WebsocketFrameSchema.parse({
    frameId,
    correlationId: frameId,
    type: "completion",
    address: "thought",
    frame: CompletionFrameChunkSchema.parse({
      id: frameId,
      object: "chat.completion",
      model: "gpt-4",
      role: "assistant",
      content,
      delta: null,
      createdTs: createTimestamp(),
      title: type,
      index: 0,
      finishReason: "stop",
      notificationType: type,
      severity,
    }),
    loading: false,
  });
};