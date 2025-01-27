"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { WebsocketFrameType, MediaContent } from "@/lib/types";
import { format } from "date-fns";
import { Loader2, Image as ImageIcon, Video, Music, FileText, Link2, Code, Copy, Check } from "lucide-react";
import Prism from "prismjs";
import "prismjs/components/prism-typescript";
import "prismjs/components/prism-javascript";
import "prismjs/components/prism-jsx";
import "prismjs/components/prism-tsx";
import "prismjs/components/prism-css";
import "prismjs/components/prism-json";
import ReactMarkdown from "react-markdown";
import { useState, useCallback } from "react";
import { Button } from "../ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";

interface MessageBubbleProps {
  message: WebsocketFrameType;
}

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code, language]);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [code]);

  const finalLanguage = language || 'typescript';

  return (
    <div className="rounded-md overflow-hidden my-2 border w-full max-w-2xl">
      <div className="flex items-center justify-between px-4 py-2 bg-muted border-b">
        <div className="flex items-center gap-2">
          <Code className="h-4 w-4" />
          {language && (
            <span className="text-sm font-medium">{language}</span>
          )}
        </div>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={handleCopy}
            >
              {copied ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span className="sr-only">Copy code</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{copied ? 'Copied!' : 'Copy code'}</p>
          </TooltipContent>
        </Tooltip>
      </div>
      <div className="p-4 overflow-x-auto bg-card">
        <pre className="m-0" suppressHydrationWarning>
          <code
            ref={codeRef}
            className={`language-${finalLanguage}`}
            suppressHydrationWarning
          >
            {code || 'No code provided'}
          </code>
        </pre>
      </div>
    </div>
  );
}

function MediaPreview({ media }: { media: MediaContent }) {
  const commonClasses = "rounded-md overflow-hidden my-2 border";

  switch (media.type) {
    case 'image':
      return (
        <div className={cn(commonClasses, "max-w-sm")}>
          <div className="aspect-video relative bg-muted flex items-center justify-center">
            {media.url ? (
              <img
                src={media.url}
                alt={media.title || "Image"}
                className="object-cover w-full h-full"
              />
            ) : (
              <ImageIcon className="h-8 w-8 text-muted-foreground" />
            )}
          </div>
          {media.title && (
            <div className="p-2 text-sm bg-card">
              <p className="truncate">{media.title}</p>
            </div>
          )}
        </div>
      );

    case 'video':
      return (
        <div className={cn(commonClasses, "max-w-sm")}>
          <div className="aspect-video relative bg-muted flex items-center justify-center">
            {media.url ? (
              <video
                src={media.url}
                controls
                className="w-full h-full"
                poster={media.thumbnail}
              >
                Your browser does not support the video tag.
              </video>
            ) : (
              <Video className="h-8 w-8 text-muted-foreground" />
            )}
          </div>
          {media.title && (
            <div className="p-2 text-sm bg-card">
              <p className="truncate">{media.title}</p>
              {media.duration && (
                <p className="text-xs text-muted-foreground">
                  Duration: {Math.floor(media.duration / 60)}:{String(media.duration % 60).padStart(2, '0')}
                </p>
              )}
            </div>
          )}
        </div>
      );

    case 'audio':
      return (
        <div className={cn(commonClasses, "w-full max-w-sm bg-card")}>
          <div className="p-4 flex items-center gap-4">
            <Music className="h-8 w-8 text-muted-foreground shrink-0" />
            <div className="min-w-0 flex-1">
              {media.title && <p className="truncate font-medium">{media.title}</p>}
              {media.url ? (
                <audio controls className="w-full mt-2">
                  <source src={media.url} type={media.mimeType} />
                  Your browser does not support the audio element.
                </audio>
              ) : (
                <p className="text-sm text-muted-foreground">Audio preview not available</p>
              )}
            </div>
          </div>
        </div>
      );

    case 'code':
      return <CodeBlock code={media.code || ''} language={media.language} />;

    case 'file':
      return (
        <div className={cn(commonClasses, "w-full max-w-sm bg-card")}>
          <div className="p-4 flex items-center gap-4">
            <FileText className="h-8 w-8 text-muted-foreground shrink-0" />
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{media.title || 'Untitled File'}</p>
              {media.size && (
                <p className="text-sm text-muted-foreground">
                  {(media.size / 1024 / 1024).toFixed(2)} MB
                </p>
              )}
            </div>
          </div>
        </div>
      );

    case 'link':
      return (
        <div className={cn(commonClasses, "w-full max-w-sm bg-card")}>
          <div className="p-4 flex items-center gap-4">
            <Link2 className="h-6 w-6 text-muted-foreground shrink-0" />
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{media.title || media.url}</p>
              {media.url && (
                <a
                  href={media.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline truncate block"
                >
                  {media.url}
                </a>
              )}
            </div>
          </div>
        </div>
      );

    default:
      return null;
  }
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.frame.role === "user";

  return (
    <div
      className={cn(
        "flex",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">
            {isUser ? "You" : "AI Assistant"}
          </span>
          {message.loading && (
            <Loader2 className="h-4 w-4 animate-spin" />
          )}
        </div>
        <div className="mt-1 prose prose-sm max-w-none">
          <ReactMarkdown>{message.frame.content || ''}</ReactMarkdown>
        </div>
        {message.frame.media && message.frame.media.length > 0 && (
          <div className="space-y-2 mt-2">
            {message.frame.media.map((media, index) => (
              <MediaPreview key={index} media={media} />
            ))}
          </div>
        )}
        <time className="text-xs text-muted-foreground block mt-2">
          {format(new Date(message.frame.createdTs * 1000), "HH:mm")}
        </time>
      </div>
    </div>
  );
}