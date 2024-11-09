"use client";

import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import {
  createContext,
  ReactNode,
  useState,
  useContext,
} from "react";

type ArtifactContextType = {
  artifacts: CompletionFrameChunk[];
  setArtifacts: (artifact: CompletionFrameChunk[]) => void;
};

const ArtifactContext = createContext<ArtifactContextType>({
  artifacts: [],
  setArtifacts: () => {},
});

export const ArtifactProvider = ({ children }: { children: ReactNode }) => {
  const [artifacts, setArtifacts] = useState<CompletionFrameChunk[]>([]);


  return (
    <ArtifactContext.Provider value={{ artifacts, setArtifacts }}>
      {children}
    </ArtifactContext.Provider>
  );
};

// Custom hook for easier context usage
export const useArtifact = () => {
  const context = useContext(ArtifactContext);
  if (context === undefined) {
    throw new Error("useArtifact must be used within an ArtifactProvider");
  }
  return context;
};

export default ArtifactContext;
