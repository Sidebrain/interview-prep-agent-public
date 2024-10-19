"use client";
import { forwardRef, useEffect, useState } from "react";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { RoutingKeyType } from "@/types/websocketTypes";
import clientLogger from "@/app/lib/clientLogger";

type HTMLTextAreaElementProps = {
  inputValue: string;
  onInputChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onStructuredKeyDown: (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
    routingKey: RoutingKeyType
  ) => void;
  onSubmit: (e: React.FormEvent) => void;
  onStructuredSubmit: (e: React.FormEvent, routingKey: RoutingKeyType) => void;
  maxHeight: number;
  // voice: VoiceHookParams;
  getPermissionsAndStartRecording: () => Promise<void>;
  stopRecording: () => void;
  isRecording: boolean;
  playRecording: () => void;
  stopPlaying: () => void;
};

const UserInputInterface = forwardRef<
  HTMLTextAreaElement,
  HTMLTextAreaElementProps
>(
  (
    {
      inputValue,
      onInputChange,
      maxHeight,
      onKeyDown,
      onStructuredKeyDown,
      // onSubmit,
      onStructuredSubmit,
      getPermissionsAndStartRecording,
      stopRecording,
      isRecording,
      playRecording,
      stopPlaying,
    },
    ref
  ) => {
    const [isStructured, setIsStructured] =
      useState<RoutingKeyType>("streaming");
    //
    function adjustTextareaHeight() {
      if (ref && typeof ref !== "function" && ref.current) {
        ref.current.style.height = "auto";
        const newHeight = Math.min(ref.current.scrollHeight, maxHeight);
        ref.current.style.height = `${newHeight}px`;
      }
    }

    function handleInputChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
      onInputChange(e.target.value);
      adjustTextareaHeight();
    }

    useEffect(adjustTextareaHeight, [inputValue, maxHeight]);

    return (
      <div className="bg-white p-2 flex flex-col gap-2">
        <div className="flex gap-2 items-center justify-center ">
          <label className="text-gray-800 text-bold">Structured</label>
          <Checkbox
            onCheckedChange={() =>
              setIsStructured(
                isStructured === "streaming" ? "structured" : "streaming"
              )
            }
          />
        </div>
        <form
          onSubmit={(e) => onStructuredSubmit(e, isStructured)}
          className="flex"
        >
          <Textarea
            ref={ref}
            value={inputValue}
            // onKeyDown={onKeyDown}
            onKeyDown={(e) => onStructuredKeyDown(e, isStructured)}
            onChange={handleInputChange}
            placeholder="Type a message..."
            className="flex-grow p-2 border rounded-lg resize-none mr-2"
            style={{ maxHeight: `${maxHeight}px` }}
            rows={1}
          />

          <div className="flex flex-col gap-2">
            <Button type="submit" className="self-end">
              Send
            </Button>
            <Button
              onClick={(e) => {
                e.preventDefault();
                if (isRecording) {
                  clientLogger.debug("Stopping recording");
                  stopRecording();
                } else {
                  getPermissionsAndStartRecording();
                }
              }}
              type="button"
              className="self-end"
            >
              {isRecording ? "Stop" : "Record"}
            </Button>
            <Button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                playRecording();
              }}
            >{`Play`}</Button>
          </div>
        </form>
      </div>
    );
  }
);

export default UserInputInterface;
