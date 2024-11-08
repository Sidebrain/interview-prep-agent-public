"use client";

import { createContext, ReactNode, useState, useContext } from "react";

type Artifact = {
  text: string | null;
  title: string | null;
} | null;

type ArtifactContextType = {
  artifact: Artifact;
  setArtifact: (artifact: Artifact) => void;
};

const ArtifactContext = createContext<ArtifactContextType>({
  artifact: null,
  setArtifact: () => {},
});

export const ArtifactProvider = ({ children }: { children: ReactNode }) => {
  const [artifact, setArtifact] = useState<Artifact>(null);

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

export type { Artifact };

export default ArtifactContext;
