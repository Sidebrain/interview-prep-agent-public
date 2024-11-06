"use client";
import { InputProvider } from "@/context/InputContext";
import UserArea from "./components/UserArea";
import useWebSocket from "@/hooks/useWebsocketNew";
import { useEffect, useState } from "react";
import clientLogger from "@/app/lib/clientLogger";
import GenerativeArea2 from "./components/GenerativeArea2";
import { ArtifactProvider } from "@/context/ArtefactContext";

export default function InteractionArea() {
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  // hooks here
  const { frameList, sendMessage, frameHandler } = useWebSocket({
    url: wsUrl || "",
    enabled: !!wsUrl,
  });

  clientLogger.debug("ws url", process.env.NEXT_PUBLIC_WS_URL_V2);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (process.env.NEXT_PUBLIC_WS_URL_V2) {
        console.log("Setting WS URL:", process.env.NEXT_PUBLIC_WS_URL_V2);
        setWsUrl(process.env.NEXT_PUBLIC_WS_URL_V2);
      } else {
        console.warn("WS URL not found in env vars:", process.env);
      }
    }, 100);

    clientLogger.debug("ws url", process.env.NEXT_PUBLIC_WS_URL_V2);
    return () => clearTimeout(timer);
  }, []);

  if (!wsUrl) {
    return <div>Waiting for websocket url</div>;
  }

  return (
    <div className="w-full flex p-2">
      <InputProvider>
        <ArtifactProvider>
        <UserArea
          frameList={frameList}
          sendMessage={sendMessage}
          frameHandler={frameHandler}
        />
        {/* <GenerativeArea frameList={frameList} artefactText={artefactText} /> */}
          <GenerativeArea2 />
        </ArtifactProvider>
      </InputProvider>
    </div>
  );
}
