import * as React from "react";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function HeaderSelect() {
  return (
    <Select defaultValue="openai-gpt">
      <SelectTrigger className="w-[180px] bg-white h-6">
        <SelectValue placeholder="Select a model" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Models</SelectLabel>
          <SelectItem value="openai-gpt">OpenAI GPT</SelectItem>
          <SelectItem value="claude">Claude</SelectItem>
          <SelectItem value="davinci">Davinci</SelectItem>
          <SelectItem value="curie">Curie</SelectItem>
          <SelectItem value="babbage">Babbage</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
