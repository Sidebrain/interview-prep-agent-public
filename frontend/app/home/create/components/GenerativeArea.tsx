"use client";
import { FrameType } from "@/reducers/messageFrameReducer";
import React, { useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";

type GenerativeAreaProps = {
  frameList: FrameType[];
};

const ArtefactFrames = (props: { frameList: FrameType[] }) => {
  const renderArtefactFrame = useCallback(
    (frame: FrameType) =>
      frameRenderHandler({ frame: frame, address: "artefact" }),
    [props.frameList]
  );
  return <>{props.frameList.map((frame) => renderArtefactFrame(frame))}</>;
};

const GenerativeArea = (props: GenerativeAreaProps) => {
  return (
    <div className="w-full bg-gray-100 h-full flex flex-col items-center overflow-scroll">
      <ArtefactFrames frameList={props.frameList} />
    </div>
  );
};

export default GenerativeArea;
