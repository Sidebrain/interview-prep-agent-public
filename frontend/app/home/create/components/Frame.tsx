import { FrameType } from "@/reducers/messageFrameReducer";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";
import { useArtifact } from "@/context/ArtefactContext";
import { Button } from "@/components/ui/button";

type FrameProps = {
  frame: FrameType;
};

const Frame = ({ frame }: FrameProps) => {
  const { setArtifactText } = useArtifact();

  const handleArtifactClick = (artifactText: string) => {
    setArtifactText(artifactText);
  };
  return (
    <div className="flex flex-col gap-2">
      {/* Content frame is always rendered */}
      {frameRenderHandler({ frame, address: "content" })}
      {/* Artefact frames rendered if available */}
      {frame.artefactFrames?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {frame.artefactFrames.map((artefact, idx) => {
            return (
              <Button
                className="bg-green-500 p-4 rounded-md"
                key={idx}
                onClick={(e) => {
                  e.preventDefault();
                  handleArtifactClick(artefact.content || "");
                }}
              >
                {artefact.content?.slice(0, 50)}
              </Button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Frame;
