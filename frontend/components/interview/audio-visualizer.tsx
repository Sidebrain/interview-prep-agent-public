"use client";

import { useEffect, useRef } from 'react';
import { cn } from "@/lib/utils";

interface AudioVisualizerProps {
  isRecording: boolean;
  className?: string;
}

export function AudioVisualizer({ isRecording, className }: AudioVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    async function setupAudioContext() {
      try {
        if (!audioContextRef.current) {
          audioContextRef.current = new AudioContext();
        }

        if (!mediaStreamRef.current) {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaStreamRef.current = stream;
          
          const source = audioContextRef.current.createMediaStreamSource(stream);
          const analyzer = audioContextRef.current.createAnalyser();
          
          // Increase FFT size for smoother visualization
          analyzer.fftSize = 1024;
          analyzer.smoothingTimeConstant = 0.85;
          
          source.connect(analyzer);
          analyzerRef.current = analyzer;
        }
        
        startVisualization();
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    }

    function startVisualization() {
      if (!canvasRef.current || !analyzerRef.current) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Set canvas size to match display size
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const analyzer = analyzerRef.current;
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      function draw() {
        if (!isRecording) {
          // Draw flat line with subtle animation when not recording
          ctx.fillStyle = 'rgb(241, 245, 249)';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          
          const time = Date.now() / 1000;
          ctx.beginPath();
          ctx.strokeStyle = 'rgb(203, 213, 225)';
          ctx.lineWidth = 2;
          
          for (let x = 0; x < canvas.width; x++) {
            const y = (Math.sin(x * 0.02 + time) * 2) + canvas.height / 2;
            if (x === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          }
          
          ctx.stroke();
          requestAnimationFrame(draw);
          return;
        }

        animationFrameRef.current = requestAnimationFrame(draw);
        analyzer.getByteTimeDomainData(dataArray);

        // Clear background with gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, 'rgb(241, 245, 249)');
        gradient.addColorStop(1, 'rgb(248, 250, 252)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw waveform
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'rgb(37, 99, 235)';
        ctx.beginPath();

        const sliceWidth = (canvas.width / bufferLength) * 2;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * canvas.height) / 2;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }

          x += sliceWidth;
        }

        // Add glow effect
        ctx.shadowColor = 'rgba(37, 99, 235, 0.2)';
        ctx.shadowBlur = 15;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Draw center line
        ctx.beginPath();
        ctx.strokeStyle = 'rgba(37, 99, 235, 0.1)';
        ctx.moveTo(0, canvas.height / 2);
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
      }

      draw();
    }

    if (isRecording) {
      setupAudioContext();
    } else {
      startVisualization(); // Keep animation running for idle state
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return (
    <div className="relative w-full">
      <canvas
        ref={canvasRef}
        className={cn(
          "w-full h-20 rounded-md bg-slate-50 transition-opacity duration-200",
          isRecording ? "opacity-100" : "opacity-75",
          className
        )}
      />
      {isRecording && (
        <div className="absolute left-3 top-2 text-xs font-medium text-blue-600 animate-pulse">
          Recording...
        </div>
      )}
    </div>
  );
}