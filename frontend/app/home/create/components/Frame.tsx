import { FrameType } from "@/reducers/messageFrameReducer";
import { frameRenderHandler } from "@/handlers/frameRenderHandler";

type FrameProps = {
  frame: FrameType;
};

const Frame = ({ frame }: FrameProps) => {
  return (
    <div className="flex flex-col gap-2">
      {/* Content frame is always rendered */}
      {frameRenderHandler({ frame, address: "content" })}

      {/* Artefact frames are optional */}
      {frame.artefactFrames?.length > 0 && (
        <div className="flex flex-col gap-2">
          {frame.artefactFrames.map((artefact, idx) => {
            const previewText =
              artefact.content?.split("\n")[0].slice(0, 50) + "...";
            return (
              <details
                key={idx}
                className="border border-gray-400 p-2 m-2 rounded cursor-pointer"
              >
                <summary className="font-medium text-sm hover:text-blue-600">
                  {previewText}
                </summary>
                {frameRenderHandler({
                  frame: {
                    ...frame,
                    artefactFrames: [artefact],
                  },
                  address: "artefact",
                })}
              </details>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Frame;
