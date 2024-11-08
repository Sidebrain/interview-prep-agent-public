import { FrameType } from "@/types/reducerTypes";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import { useArtifact } from "@/context/ArtifactContext";
import { Button } from "@/components/ui/button";
import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";

type FrameProps = {
  frame: FrameType;
};

const Frame = ({ frame }: FrameProps) => {
  const { setArtifact } = useArtifact();

  const handleArtifactClick = (frame: CompletionFrameChunk) => {
    setArtifact(frame);
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Content frame is always rendered */}
      {frameRenderHandler({ frame, address: "content" })}
      {/* Artifact frames rendered if available */}
      {frame.artifactFrames?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {frame.artifactFrames.map((artifact, idx) => {
            return (
              <Button
                className="bg-green-500 p-4 rounded-md"
                key={idx}
                onClick={(e) => {
                  e.preventDefault();
                  handleArtifactClick(artifact);
                }}
              >
                {artifact.title || artifact.content?.slice(0, 50)}
              </Button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Frame;
