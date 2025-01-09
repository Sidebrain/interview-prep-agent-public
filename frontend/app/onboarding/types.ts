import { WebsocketFrame, WebsocketFrameSchema } from "@/types/ScalableWebsocketTypes";
import { z } from "zod";

export type Interviewer = {
  _id: string; // UUID stored as string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  job_description: string;
  rating_rubric: string;
  question_bank: string;
  memory: WebsocketFrame[];
}

export interface CandidateRequest {
  name: string;
  email: string;
  phone_number: string;
}

export const CandidateSchema = z.object({
  _id: z.string().uuid(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
  name: z.string(),
  email: z.string().email(),
  phone_number: z.string(),
  memory: z.array(WebsocketFrameSchema)
});

export type Candidate = z.infer<typeof CandidateSchema>;

