import type { FrameType } from "@/types/reducerTypes";
import { FrameRenderHandler } from "@/handlers/frameRenderHandler";
import { useArtifact } from "@/context/ArtifactContext";
import { Button } from "@/components/ui/button";
import { useCallback, useEffect } from "react";
import { cn } from "@/lib/utils";
import { RefreshCcw } from "lucide-react";

type FrameProps = {
  frame: FrameType;
};

const Frame = ({ frame }: FrameProps) => {
  const { setFocus, setFrameId, artifactObject, regeneratingTitle } =
    useArtifact();

  const renderArtifactButtons = useCallback(() => {
    return Object.entries(artifactObject).map(([title, frames], idx) => {
      const isRegenerating = regeneratingTitle === title;

      return (
        <Button
          className="bg-green-500 p-4 rounded-md relative"
          key={idx}
          onClick={() => setFocus({ title, index: 0 })}
        >
          {title}
          <span
            className={cn(
              "absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
            )}
          >
            {isRegenerating ? (
              <RefreshCcw className="h-3 w-3 animate-spin" />
            ) : (
              frames.length
            )}
          </span>
        </Button>
      );
    });
  }, [artifactObject, setFocus, regeneratingTitle]);

  useEffect(() => {
    setFrameId(frame.frameId);
  }, [frame]);

  return (
    <div className="flex flex-col gap-2">
      {/* Content frame is always rendered */}
      {FrameRenderHandler({ frame, address: "content" })}
      {/* Artifact frames rendered if available */}
      {frame.artifactFrames.length > 0 &&
        Object.keys(artifactObject).length > 0 && (
          <div className="flex flex-wrap gap-2">{renderArtifactButtons()}</div>
        )}
    </div>
  );
};

export default Frame;
