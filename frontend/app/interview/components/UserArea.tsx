import { useWebsocketContext } from "../context/WebsocketContext";
import MessageFrame from "./MessageFrame";

const UserArea = () => {
  const { state: frameList } = useWebsocketContext();
  return (
    <div>
      {frameList.frames.map((frame, index) => (
        <MessageFrame key={index} frame={frame} />
      ))}
    </div>
  );
};

export default UserArea;
