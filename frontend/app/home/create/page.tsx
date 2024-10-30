"use client";
import { InputProvider } from "@/context/InputContext";
import UserArea from "./components/UserArea";
import GenerativeArea from "./components/GenerativeArea";
import useWebSocket from "@/hooks/useWebsocketNew";

export default function InteractionArea() {
  // hooks here
  const { frameList, sendMessage, frameHandler } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL_V2 as string,
  });

  return (
    <div className="w-full flex p-2">
      <InputProvider>
        <UserArea
          frameList={frameList}
          sendMessage={sendMessage}
          frameHandler={frameHandler}
        />
        <GenerativeArea frameList={frameList} />
      </InputProvider>
    </div>
  );
}
