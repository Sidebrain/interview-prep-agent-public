"use client";

import { useState, useCallback } from "react";
// import { TextInputArea } from "./text-input-area";
// import { VoiceInputArea } from "./voice-input-area";
import { useVoiceRecognition } from "@/hooks/use-voice-recognition";
import { Keyboard, Mic, Send, X } from "lucide-react";
import { Button } from "../ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import { Textarea } from "../ui/textarea";
import UserInputArea from "@/app/shared/components/UserInputArea";

type InputPanelProps = {
  maxTextareaHeight: number;
};

export function InputPanel({ maxTextareaHeight }: InputPanelProps) {
  return (
    <div className="fixed bottom-0 left-0 right-80 bg-background border-t p-4">
      <UserInputArea maxTextareaHeight={maxTextareaHeight} />
    </div>
  );
}

// function TextInputArea({
//   message,
//   onMessageChange,
//   onSend,
//   onModeToggle,
// }: {
//   message: string;
//   onMessageChange: (message: string) => void;
//   onSend: () => void;
//   onModeToggle: () => void;
// }) {
//   const handleKeyDown = (e: React.KeyboardEvent) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       onSend();
//     }
//   };

//   return (
//     <div className="flex gap-2">
//       <Textarea
//         value={message}
//         onChange={(e) => onMessageChange(e.target.value)}
//         onKeyDown={handleKeyDown}
//         placeholder="Type your message..."
//         className="min-h-[80px] resize-none"
//       />
//       <div className="flex flex-col gap-2">
//         <Tooltip>
//           <TooltipTrigger asChild>
//             <Button
//               variant="outline"
//               size="icon"
//               onClick={onModeToggle}
//             >
//               <Mic className="h-4 w-4" />
//               <span className="sr-only">Switch to voice input</span>
//             </Button>
//           </TooltipTrigger>
//           <TooltipContent>Switch to voice input</TooltipContent>
//         </Tooltip>
//         <Button
//           variant="default"
//           size="icon"
//           onClick={onSend}
//           disabled={!message.trim()}
//         >
//           <Send className="h-4 w-4" />
//           <span className="sr-only">Send message</span>
//         </Button>
//       </div>
//     </div>
//   );
// }

// function VoiceInputArea({
//   transcript,
//   isListening,
//   onStartListening,
//   onStopListening,
//   onModeToggle,
// }: {
//   transcript: string;
//   isListening: boolean;
//   onStartListening: () => void;
//   onStopListening: () => void;
//   onModeToggle: () => void;
// }) {
//   return (
//     <div className="flex flex-col gap-4">
//       <div className="flex items-center gap-4 min-h-[80px] bg-muted rounded-md p-4">
//         <div className="flex-1">
//           {isListening ? (
//             <p className="text-muted-foreground animate-pulse">
//               Listening... {transcript}
//             </p>
//           ) : (
//             <p className="text-muted-foreground">
//               Press and hold space or click the microphone to speak
//             </p>
//           )}
//         </div>
//         <div className="flex gap-2">
//           <Tooltip>
//             <TooltipTrigger asChild>
//               <Button
//                 variant="outline"
//                 size="icon"
//                 onClick={onModeToggle}
//               >
//                 <Keyboard className="h-4 w-4" />
//                 <span className="sr-only">Switch to text input</span>
//               </Button>
//             </TooltipTrigger>
//             <TooltipContent>Switch to text input</TooltipContent>
//           </Tooltip>
//           <Button
//             variant={isListening ? "destructive" : "default"}
//             size="icon"
//             onClick={isListening ? onStopListening : onStartListening}
//           >
//             {isListening ? (
//               <X className="h-4 w-4" />
//             ) : (
//               <Mic className="h-4 w-4" />
//             )}
//             <span className="sr-only">
//               {isListening ? "Stop recording" : "Start recording"}
//             </span>
//           </Button>
//         </div>
//       </div>
//       {/* <AudioVisualizer isRecording={isListening} /> */}
//     </div>
//   );
// }
