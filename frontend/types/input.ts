import { z } from "zod";

export const InputZodFields = z.object({
  role: z.string(),
  companyName: z.string(),
  teamName: z.string(),
  requirements: z.string().optional(),
});

export type InputFields = z.infer<typeof InputZodFields>;
