"use client";

import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import { createContext, ReactNode, useState, useContext } from "react";


type ArtifactContextType = {
  artifact: CompletionFrameChunk | null;
  setArtifact: (artifact: CompletionFrameChunk | null) => void;
};

const ArtifactContext = createContext<ArtifactContextType>({
  artifact: null,
  setArtifact: () => {},
});

export const ArtifactProvider = ({ children }: { children: ReactNode }) => {
  const [artifact, setArtifact] = useState<CompletionFrameChunk | null>(null);

  return (
    <ArtifactContext.Provider value={{ artifact, setArtifact }}>
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
