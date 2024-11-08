"use client";
import React, { useCallback } from "react";
import { Artifact, useArtifact } from "@/context/ArtifactContext";
import Markdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { X, Copy, Download, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

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
};

const BottomButtonTray = ({ onCopy, onDownload }: BottomButtonTrayProps) => {
  return (
    <div className="flex justify-end gap-2 p-1 bg-gray-200 border-t sticky bottom-0 z-10">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => console.log("regenerate clicked")}
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
  );
};

const ArtifactFrame = () => {
  const { artifact, setArtifact } = useArtifact();

  const handleCopyArtifact = async () => {
    if (!artifact?.text) return;
    try {
      await navigator.clipboard.writeText(artifact?.text || "");
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleDownloadArtifact = () => {
    if (!artifact?.text) return;
    const blob = new Blob([artifact.text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "artifact.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderArtifactFrame = useCallback(
    (artifact: Artifact) => {
      if (!artifact) return null;
      return (
        <div className="w-full bg-white rounded-lg shadow-lg max-w-4xl mx-auto my-2 flex flex-col h-full">
          <TopButtonTray
            onClose={() => setArtifact(null)}
            title={artifact.title || ""}
          />

          {/* Content - scrollable */}
          <div className="flex-1 overflow-auto min-h-0">
            <div className="p-6">
              <Markdown
                remarkPlugins={[remarkGfm]}
                className="markdown-content break-words text-sm"
                components={components}
              >
                {artifact.text}
              </Markdown>
            </div>
          </div>

          <BottomButtonTray
            onCopy={handleCopyArtifact}
            onDownload={handleDownloadArtifact}
          />
        </div>
      );
    },
    [artifact, setArtifact]
  );

  return <>{renderArtifactFrame(artifact)}</>;
};

export default ArtifactFrame;
