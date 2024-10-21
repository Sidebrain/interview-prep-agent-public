import { useEffect, useRef } from "react";

type MessageContainerProps = {
  setMaxTextareaHeight: (maxTextareaHeight: number) => void;
};

function MessageContainer(props: MessageContainerProps) {
  const containerAreaRef = useRef<HTMLDivElement>(null); // to calculate div height for textarea sizing

  // identify the max textarea height
  useEffect(() => {
    function computeMaxHeight() {
      if (containerAreaRef.current) {
        const containerHeight = containerAreaRef.current.clientHeight;
        const newMaxHeight = Math.max(50, Math.max(150, containerHeight * 0.7));
        console.log("newMaxHeight: ", newMaxHeight);
        console.log("containerHeight: ", containerHeight);
        props.setMaxTextareaHeight(newMaxHeight);
      }
    }
    computeMaxHeight();

    window.addEventListener("resize", computeMaxHeight);
    return () => window.removeEventListener("resize", computeMaxHeight);
  }, []);
  return (
    <div ref={containerAreaRef} className="flex flex-col grow gap-2">
      <div className="bg-white p-2 rounded-lg">Message 1</div>
      <div className="bg-white p-2 rounded-lg">Message 2</div>
    </div>
  );
}

export default MessageContainer;
