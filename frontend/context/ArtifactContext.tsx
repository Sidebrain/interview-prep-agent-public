"use client";

import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import {
  createContext,
  ReactNode,
  useState,
  useContext,
  useEffect,
  useCallback,
} from "react";
import { useWebsocketContext } from "./WebsocketContext";
import clientLogger from "@/app/lib/clientLogger";

type ArtifactStateType = {
  [title: string]: CompletionFrameChunk[];
};

type ArtifactContextType = {
  artifactObject: ArtifactStateType;
  frameId: string;
  setFrameId: (frameId: string) => void;
  focus: FocusType;
  setFocus: (focus: FocusType) => void;
};

type FocusType = {
  title: string;
  index: number | null;
};

const ArtifactContext = createContext<ArtifactContextType>({
  artifactObject: {},
  frameId: "",
  setFrameId: () => {},
  focus: {
    title: "",
    index: null,
  },
  setFocus: () => {},
});

export const ArtifactProvider = ({ children }: { children: ReactNode }) => {
  const { frameList } = useWebsocketContext();
  const [artifactObject, setArtifactObject] = useState<ArtifactStateType>({});
  const [frameId, setFrameId] = useState("");
  const [focus, setFocus] = useState<FocusType>({
    title: "",
    index: null,
  });

  const buildArtifactObject = useCallback(() => {
    console.log("buildArtifactObject triggered");
    const focusFrame = frameList.find((frame) => frame.frameId === frameId);
    if (!focusFrame) return;

    setArtifactObject({});

    const uniqueTitles = Array.from(
      new Set(focusFrame.artifactFrames.map((frame) => frame.title))
    );
    uniqueTitles.forEach((title) => {
      if (!title) return;

      // frames with a certain title, sorted by created timestamp
      const framesWithThisTitle = focusFrame.artifactFrames
        .filter((frame) => frame.title === title)
        .sort((a, b) => a.createdTs - b.createdTs);

      setArtifactObject((prev) => ({ ...prev, [title]: framesWithThisTitle }));
    });
    clientLogger.debug("artifactObject built up: ", artifactObject);
  }, [frameId, frameList]);

  useEffect(() => {
    console.log("frameId changed to: ", frameId);
    if (frameId) {
      buildArtifactObject();
    }
  }, [frameId, buildArtifactObject, frameList]);

  return (
    <ArtifactContext.Provider
      value={{ artifactObject, frameId, setFrameId, focus, setFocus }}
    >
      {children}
    </ArtifactContext.Provider>
  );
};

export const useArtifact = () => {
  const context = useContext(ArtifactContext);
  if (context === undefined) {
    throw new Error("useArtifact must be used within an ArtifactProvider");
  }
  return context;
};
