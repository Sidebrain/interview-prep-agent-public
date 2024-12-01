import { Button } from "@/components/ui/button";
import { useWebsocketContext } from "../context/WebsocketContext";
import useVoiceTranscription from "../hooks/useVoiceTranscription";
import MessageFrame from "./MessageFrame";
import { useState } from "react";

const AudioPlayer = ({ url }: { url: string }) => {
  return <audio src={url} controls style={{ width: "100%" }} autoPlay />;
};

const UserArea = () => {
  // const { state: frameList } = useWebsocketContext();
  const {
    isRecording,
    error,
    startRecording,
    stopRecording,
    transcribeAudio,
    playbackUrl,
  } = useVoiceTranscription({
    onTranscription: ({ transcription }) => {
      console.log(transcription);
    },
  });
  return (
    <div>
      {/* {frameList.frames.map((frame, index) => (
        <MessageFrame key={index} frame={frame} />
      ))} */}
      <Button onClick={startRecording}>Start Recording</Button>
      <Button onClick={stopRecording}>Stop Recording</Button>

      {playbackUrl && <AudioPlayer url={playbackUrl} />}
      {error && <p>{error}</p>}
      {isRecording && <p>Recording...</p>}
      <Button onClick={transcribeAudio}>Transcribe Audio</Button>
    </div>
  );
};

export default UserArea;
