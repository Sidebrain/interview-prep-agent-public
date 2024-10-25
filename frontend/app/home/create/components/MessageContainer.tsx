import clientLogger from "@/app/lib/clientLogger";
import { FrameType } from "@/reducers/messageFrameReducer";
import { useCallback, useEffect, useRef } from "react";

type MessageContainerProps = {
  setMaxTextareaHeight: (maxTextareaHeight: number) => void;
  frameList: FrameType[];
};

function MessageContainer(props: MessageContainerProps) {
  const containerAreaRef = useRef<HTMLDivElement>(null); // to calculate div height for textarea sizing

  // for rendering the frames
  const renderFrames = useCallback(
    (frameList: FrameType[]) => {
      return frameList.map((frame) => (
        <div
          key={frame.frameId}
          className="flex text-sm flex-col bg-green-200 rounded-sm p-4"
        >
          <div className="m-2 bg-green-300 p-8 text-left whitespace-pre-wrap rounded-md">
            {frame.contentFrame.content}
          </div>
          <div className="m-2 bg-green-300 p-8 text-left whitespace-pre-wrap rounded-s-lg">
            {frame.artefactFrames.length === 0 && "artifact text here"}
          </div>
        </div>
      ));
    },
    [props.frameList]
  );

  // identify the max textarea height
  useEffect(() => {
    function computeMaxHeight() {
      if (containerAreaRef.current) {
        const containerHeight = containerAreaRef.current.clientHeight;
        const newMaxHeight = Math.max(50, Math.max(150, containerHeight * 0.7));
        clientLogger.debug("newMaxHeight: ", newMaxHeight);
        clientLogger.debug("containerHeight: ", containerHeight);
        props.setMaxTextareaHeight(newMaxHeight);
      }
    }
    computeMaxHeight();

    window.addEventListener("resize", computeMaxHeight);
    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);
  return (
    <div
      ref={containerAreaRef}
      className="flex flex-col grow gap-2 overflow-auto no-scrollbar mx-36"
    >
      {renderFrames(props.frameList)}
    </div>
  );
}

export default MessageContainer;
