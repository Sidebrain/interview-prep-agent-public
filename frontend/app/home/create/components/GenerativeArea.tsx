"use client";
import { FrameType } from "@/reducers/messageFrameReducer";
import React, { useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";

const Tablist = () => (
  <Tabs defaultValue="account" className="w-full p-2 h-full">
    <TabsList className="w-full">
      <TabsTrigger value="account" className="w-full">
        Thoughts
      </TabsTrigger>
      <TabsTrigger value="password" className="w-full">
        Artefacts
      </TabsTrigger>
    </TabsList>
    <TabsContent value="thoughts" className="h-full"></TabsContent>
    <TabsContent value="artefacts" className="h-full">
      Change your password here.
    </TabsContent>
  </Tabs>
);

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

const ThoughtFrames = (props: { frameList: FrameType[] }) => {
  const renderThoughtFrame = useCallback(
    (frame: FrameType) =>
      frameRenderHandler({ frame: frame, address: "thought" }),
    [props.frameList]
  );
  return <>{props.frameList.map((frame) => renderThoughtFrame(frame))}</>;
};

const GenerativeArea = (props: GenerativeAreaProps) => {
  return (
    <div className="w-full bg-gray-100 h-full flex flex-col items-center overflow-scroll">
      <Tabs defaultValue="thoughts" className="w-full p-2 h-full sticky">
        <TabsList className="w-full ">
          <TabsTrigger value="thoughts" className="w-full">
            Thoughts
          </TabsTrigger>
          <TabsTrigger value="artefacts" className="w-full">
            Artefacts
          </TabsTrigger>
        </TabsList>
        <TabsContent value="thoughts" className="h-full ">
          <ThoughtFrames frameList={props.frameList} />
        </TabsContent>
        <TabsContent value="artefacts" className="h-full ">
          <ArtefactFrames frameList={props.frameList} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default GenerativeArea;
