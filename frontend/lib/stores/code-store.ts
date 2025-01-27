import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SupportedLanguage } from "@/components/code-editor/languages";

interface CodeState {
  code: string;
  language: SupportedLanguage;
  setCode: (code: string) => void;
  setLanguage: (language: SupportedLanguage) => void;
}

export const useCodeStore = create<CodeState>()(
  persist(
    (set) => ({
      code: "// Write your code here\n",
      language: "typescript",
      setCode: (code) => set({ code }),
      setLanguage: (language) => set({ language }),
    }),
    {
      name: "code-store",
    }
  )
);