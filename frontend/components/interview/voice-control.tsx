'use client';

import { useEffect, useState } from 'react';
import { Button } from '../ui/button';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { useVoiceRecognition } from '@/hooks/use-voice-recognition';
import { useInterviewStore } from '@/lib/stores/interview-store';
import { cn } from '@/lib/utils';

export function VoiceControl() {
  const { isListening, startListening, stopListening, transcript } =
    useVoiceRecognition();
  const addMessage = useInterviewStore((state) => state.addMessage);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !isListening && !isProcessing) {
        e.preventDefault();
        startListening();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isListening, isProcessing, startListening]);

  const handleVoiceToggle = async () => {
    if (isListening) {
      stopListening();
      setIsProcessing(true);

      if (transcript) {
        addMessage({
          id: Date.now().toString(),
          content: transcript,
          role: 'user',
          timestamp: new Date(),
        });

        setTimeout(() => {
          addMessage({
            id: (Date.now() + 1).toString(),
            content: 'This is a simulated AI response.',
            role: 'assistant',
            timestamp: new Date(),
          });
          setIsProcessing(false);
        }, 1000);
      } else {
        setIsProcessing(false);
      }
    } else {
      startListening();
    }
  };

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
      <Button
        size="lg"
        className={cn(
          'h-16 w-16 rounded-full shadow-lg transition-all duration-200',
          isListening && 'bg-destructive hover:bg-destructive/90',
          'aria-[busy=true]:opacity-50'
        )}
        onClick={handleVoiceToggle}
        aria-label={isListening ? 'Stop recording' : 'Start recording'}
        aria-busy={isProcessing}
        disabled={isProcessing}
      >
        {isProcessing ? (
          <Loader2 className="h-6 w-6 animate-spin" />
        ) : isListening ? (
          <MicOff className="h-6 w-6 bg-red-200" />
        ) : (
          <Mic className="h-6 w-6" color="#3e9392" />
        )}
      </Button>
    </div>
  );
}
