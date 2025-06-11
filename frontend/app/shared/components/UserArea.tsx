import { useWebsocketContext } from "../context/WebsocketContext";
import { useState } from "react";
import MessageContainer from "./MessageContainer";

import UserInputArea from "./UserInputArea";

const UserArea = () => {
  const { state: frameList } = useWebsocketContext();
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);

  return (
    <div className="flex flex-col md:w-2/3 h-full">
      <div className="flex-1 overflow-y-auto">
        <MessageContainer
          websocketFrames={frameList.websocketFrames}
          setMaxTextareaHeight={setMaxTextareaHeight}
        />
      </div>
      <div className="flex-shrink-0">
        <UserInputArea maxTextareaHeight={maxTextareaHeight} />
      </div>
    </div>
  );
};

export default UserArea;
