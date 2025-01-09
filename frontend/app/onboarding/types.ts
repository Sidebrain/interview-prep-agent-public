import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

export type Interviewer = {
  _id: string; // UUID stored as string
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  job_description: string;
  rating_rubric: string;
  question_bank: string;
  memory: WebsocketFrame[];
}
