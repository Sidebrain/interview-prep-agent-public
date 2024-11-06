"use client";

import { createContext, ReactNode, useState, useContext } from "react";

type ArtifactContextType = {
  artifactText: string | null;
  setArtifactText: (text: string | null) => void;
};

const ArtifactContext = createContext<ArtifactContextType>({
  artifactText: null,
  setArtifactText: () => {},
});

export const ArtifactProvider = ({ children }: { children: ReactNode }) => {
  const [artifactText, setArtifactText] = useState<string | null>(null);

  return (
    <ArtifactContext.Provider value={{ artifactText, setArtifactText }}>
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