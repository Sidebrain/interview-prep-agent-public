import { z } from "zod";

export interface MessageValidator<T> {
  validate(rawData: unknown): T;
}

// Zod Validator

export class ZodMessageValidator<T> implements MessageValidator<T> {
  constructor(private schema: z.ZodType<T>) {}

  validate(rawData: unknown): T {
    return this.schema.parse(rawData);
  }
}


