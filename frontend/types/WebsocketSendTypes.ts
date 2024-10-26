import { z } from "zod";

export const ModelControlsSchema = z.object({
  model: z.string(),
  provider: z.string(),
  controls: z.object({
    temperature: z.number(),
    max_tokens: z.number(),
    top_p: z.number(),
    frequency_penalty: z.number(),
    presence_penalty: z.number(),
    stop: z.array(z.string()),
  }),
});

export const WebsocketSendTypesSchema = z.object({
  userInput: z.string(),
//   attachments: z.array(z.instanceof(Blob)),
  controls: ModelControlsSchema,
});

export type ModelControls = z.infer<typeof ModelControlsSchema>;
export type WebsocketSendTypes = z.infer<typeof WebsocketSendTypesSchema>;
