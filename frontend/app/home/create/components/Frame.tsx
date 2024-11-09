import { FrameType } from "@/types/reducerTypes";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import { useArtifact } from "@/context/ArtifactContext";
import { Button } from "@/components/ui/button";
import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import { useCallback } from 'react';

type FrameProps = {
  frame: FrameType;
};

const Frame = ({ frame }: FrameProps) => {
  const { setArtifacts } = useArtifact();

  const handleArtifactClick = (frames: CompletionFrameChunk[]) => {
    setArtifacts(frames);
  };

  const renderArtifactButtons = useCallback(() => {
    // Step 1: Get all unique titles from the artifact frames
    const uniqueTitles = Array.from(
      new Set(frame.artifactFrames.map((frame) => frame.title))
    );

    // Step 2: For each unique title, create a button that groups all frames with that title
    return uniqueTitles.map((uniqueTitle, idx) => {
      // Step 3: Get all frames that match this title
      const framesWithThisTitle = frame.artifactFrames.filter(
        (frame) => frame.title === uniqueTitle
      );

      // Step 4: Create a button for this group of frames
      return (
        <Button
          className="bg-green-500 p-4 rounded-md relative"
          key={idx}
          onClick={(e) => {
            e.preventDefault();
            // Step 5: Pass the group of frames to the click handler
            handleArtifactClick(framesWithThisTitle);
          }}
        >
          {uniqueTitle || framesWithThisTitle[0].content?.slice(0, 50)}
          <span className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {framesWithThisTitle.length}
          </span>
        </Button>
      );
    });
  }, [frame.artifactFrames, handleArtifactClick]);

  return (
    <div className="flex flex-col gap-2">
      {/* Content frame is always rendered */}
      {frameRenderHandler({ frame, address: "content" })}
      {/* Artifact frames rendered if available */}
      {frame.artifactFrames?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {renderArtifactButtons()}
        </div>
      )}
    </div>
  );
};

export default Frame;
