"use client";
import { InputProvider } from "@/context/InputContext";
import UserArea from "./components/UserArea";
import GenerativeArea from "./components/GenerativeArea";
import { ArtifactProvider } from "@/context/ArtifactContext";
import { WebsocketProvider } from "@/context/WebsocketContext";

export default function InteractionArea() {
  return (
    <div className="w-full flex p-2 justify-center">
      <WebsocketProvider
        options={{
          url: process.env.NEXT_PUBLIC_WS_URL_V2 || "",
          enabled: true,
        }}
      >
        <InputProvider>
          <ArtifactProvider>
            <UserArea />
            <GenerativeArea />
          </ArtifactProvider>
        </InputProvider>
      </WebsocketProvider>
    </div>
  );
}
