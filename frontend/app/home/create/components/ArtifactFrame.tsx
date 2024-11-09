"use client";
import React, { useCallback, useEffect, useState } from "react";
import { useArtifact } from "@/context/ArtifactContext";
import Markdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { X, Copy, Download, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CompletionFrameChunk } from "@/types/ScalableWebsocketTypes";
import { useWebsocketContext } from "@/context/WebsocketContext";

// Define the CodeProps type to fix the linter error
type CodeProps = {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
};

const components: Components = {
  code: ({ node, inline, className, children, ...props }: CodeProps) => {
    const match = /language-(\w+)/.exec(className || "");
    return !inline && match ? (
      <SyntaxHighlighter
        {...props}
        PreTag={"div"}
        language={match[1]}
        style={oneDark}
      >
        {String(children).replace(/\n$/, "")}
      </SyntaxHighlighter>
    ) : (
      <code {...props} className={className}>
        {children}
      </code>
    );
  },
};

type TopButtonTrayProps = {
  onClose: () => void;
  title: string;
};

const TopButtonTray = ({ onClose, title }: TopButtonTrayProps) => {
  return (
    <div className="flex justify-between items-center p-1 bg-gray-200 border-b rounded-t-lg sticky top-0 z-10">
      <h3 className="text-md font-semibold mx-4 truncate">{title}</h3>
      <Button
        variant="ghost"
        size="sm"
        onClick={onClose}
        className="hover:bg-gray-300"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
};

type BottomButtonTrayProps = {
  onCopy: () => void;
  onDownload: () => void;
  onRegenerate: () => void;
  numVersions: number;
  setIndex: (index: number) => void;
  index: number;
};

const BottomButtonTray = ({
  onCopy,
  onDownload,
  onRegenerate,
  numVersions,
  setIndex,
  index,
}: BottomButtonTrayProps) => {
  return (
    <div className="flex justify-between items-center">
      {
        <div className="flex gap-1 p-1">
          {[...Array(numVersions)].map((_, i) => (
            <Button
              key={i}
              variant="ghost"
              size="sm"
              onClick={() => setIndex(i)}
              className={`w-8 h-8 hover:bg-gray-300 ${
                index === i ? "bg-gray-300" : ""
              }`}
            >
              {i + 1}
            </Button>
          ))}
        </div>
      }
      <div className="flex justify-end gap-2 p-1 bg-gray-200 border-t sticky bottom-0 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={onRegenerate}
          className="hover:bg-gray-300"
        >
          <RefreshCcw className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCopy}
          className="hover:bg-gray-300"
        >
          <Copy className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onDownload}
          className="hover:bg-gray-300"
        >
          <Download className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

const ArtifactFrame = () => {
  const { sendMessage, createRegenerateSignalFrame, frameList } =
    useWebsocketContext();
  const { artifacts, setArtifacts } = useArtifact();
  const [index, setIndex] = useState(0);
  const [numVersions, setNumVersions] = useState(0);

  const handleRegenerate = () => {
    if (!artifacts.length) return;
    const regenerateFrame = createRegenerateSignalFrame(artifacts[index]);
    sendMessage(regenerateFrame);
  };

  useEffect(() => {
    setNumVersions(artifacts.length);
  }, [artifacts, handleRegenerate]);

  const handleCopyArtifact = async () => {
    if (!artifacts.length) return;
    try {
      await navigator.clipboard.writeText(artifacts[index].content || "");
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleDownloadArtifact = () => {
    if (!artifacts.length) return;
    const blob = new Blob([artifacts[index].content || ""], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "artifact.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderArtifactFrames = useCallback(
    (artifacts: CompletionFrameChunk[]) => {
      return (
        <div className="w-full bg-white rounded-lg shadow-lg max-w-4xl mx-auto my-2 flex flex-col h-full">
          <TopButtonTray
            onClose={() => setArtifacts([])}
            title={artifacts[index].title || ""}
          />

          {/* Content - scrollable */}
          <div className="flex-1 overflow-auto min-h-0">
            <div className="p-6">
              <Markdown
                remarkPlugins={[remarkGfm]}
                className="markdown-content break-words text-sm"
                components={components}
              >
                {artifacts[index].content || ""}
              </Markdown>
            </div>
          </div>

          <BottomButtonTray
            numVersions={numVersions}
            setIndex={setIndex}
            index={index}
            onCopy={handleCopyArtifact}
            onDownload={handleDownloadArtifact}
            onRegenerate={handleRegenerate}
          />
        </div>
      );
    },
    [artifacts, setArtifacts, index, numVersions]
  );

  return <>{renderArtifactFrames(artifacts)}</>;
};

export default ArtifactFrame;
