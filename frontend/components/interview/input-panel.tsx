"use client";

import { useState, useRef, useCallback } from "react";
import { Mic, Keyboard, Send, X } from "lucide-react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { useVoiceRecognition } from "@/hooks/use-voice-recognition";
import { useInterviewStore } from "@/lib/stores/interview-store";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import { AudioVisualizer } from "./audio-visualizer";
import { createMessage } from "@/lib/types";
import { createTimestamp } from "@/app/lib/helperFunctions";

export function InputPanel() {
  const [inputMode, setInputMode] = useState<"voice" | "text">("voice");
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { isListening, startListening, stopListening, transcript } = useVoiceRecognition();
  const addMessage = useInterviewStore((state) => state.addMessage);

  const handleModeToggle = () => {
    if (isListening) {
      stopListening();
    }
    setInputMode(inputMode === "voice" ? "text" : "voice");
    if (inputMode === "voice") {
      setTimeout(() => textareaRef.current?.focus(), 0);
    }
  };

  const handleSendMessage = useCallback(() => {
    const content = inputMode === "voice" ? transcript : message;
    if (!content.trim()) return;

    addMessage({
      type: "input",
      frameId: crypto.randomUUID(),
      correlationId: crypto.randomUUID(),
      address: "human",
      frame: {
        content,
        role: "user",
        title: "User Message"
      }
    });

    if (inputMode === "voice") {
      stopListening();
    } else {
      setMessage("");
    }
  }, [addMessage, inputMode, message, transcript, stopListening]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-80 bg-background border-t p-4">
      <div className="container max-w-3xl mx-auto">
        <div className="relative">
          {inputMode === "text" ? (
            <div className="flex gap-2">
              <Textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                className="min-h-[80px] resize-none"
              />
              <div className="flex flex-col gap-2">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleModeToggle}
                    >
                      <Mic className="h-4 w-4" />
                      <span className="sr-only">Switch to voice input</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Switch to voice input</TooltipContent>
                </Tooltip>
                <Button
                  variant="default"
                  size="icon"
                  onClick={handleSendMessage}
                  disabled={!message.trim()}
                >
                  <Send className="h-4 w-4" />
                  <span className="sr-only">Send message</span>
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-4 min-h-[80px] bg-muted rounded-md p-4">
                <div className="flex-1">
                  {isListening ? (
                    <p className="text-muted-foreground animate-pulse">
                      Listening... {transcript}
                    </p>
                  ) : (
                    <p className="text-muted-foreground">
                      Press and hold space or click the microphone to speak
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={handleModeToggle}
                      >
                        <Keyboard className="h-4 w-4" />
                        <span className="sr-only">Switch to text input</span>
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Switch to text input</TooltipContent>
                  </Tooltip>
                  <Button
                    variant={isListening ? "destructive" : "default"}
                    size="icon"
                    onClick={isListening ? stopListening : startListening}
                  >
                    {isListening ? (
                      <X className="h-4 w-4" />
                    ) : (
                      <Mic className="h-4 w-4" />
                    )}
                    <span className="sr-only">
                      {isListening ? "Stop recording" : "Start recording"}
                    </span>
                  </Button>
                </div>
              </div>
              <AudioVisualizer isRecording={isListening} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}