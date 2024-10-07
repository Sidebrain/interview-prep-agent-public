"use client";

import useWebSocket from "@/app/hooks/useWebsocket";
import { Button } from "../ui/button";

const SimpleChatInterface = () => {
  const { connectionStatus, lastMessage, readyState, sendMessage } =
    useWebSocket({
      url: process.env.NEXT_PUBLIC_WS_URL as string,
    });
  return (
    <div className="flex flex-col gap-8">
      <p className="bg-red-100 p-2 rounded-md">
        Status: <span>{connectionStatus}</span> <span>{readyState}</span>
      </p>
      <p className="bg-green-100 p-2 rounded-md">
        Message: <span>{lastMessage?.data}</span>
      </p>
      <Button onClick={() => sendMessage("ping")}>Send Ping</Button>
    </div>
  );
};

export default SimpleChatInterface;
