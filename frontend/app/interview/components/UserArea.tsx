import { useWebsocketContext } from "../context/WebsocketContext";
import { useState } from "react";
import MessageContainer from "./MessageContainer";

import UserInputArea from "./UserInputArea";

const UserArea = () => {
  const { state: frameList } = useWebsocketContext();
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);

  return (
    <div className="flex flex-col gap-2 items-center md:w-2/3 ">
      <MessageContainer
        websocketFrames={frameList.websocketFrames}
        setMaxTextareaHeight={setMaxTextareaHeight}
      />
      <UserInputArea maxTextareaHeight={maxTextareaHeight} />
    </div>
  );
};

export default UserArea;
