"use client";
import React, { useCallback, useEffect, useState, useRef } from "react";
import { useArtifact } from "@/context/ArtifactContext";
import Markdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { X, Copy, Download, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWebsocketContext } from "@/context/WebsocketContext";
import { cn } from "@/lib/utils";

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
  onDownload: (format: "pdf" | "md") => void;
  onRegenerate: () => void;
  isRegenerating: boolean;
  numVersions: number;
  setIndex: (index: number) => void;
  index: number;
};

const BottomButtonTray = ({
  onCopy,
  onDownload,
  onRegenerate,
  isRegenerating,
  numVersions,
  setIndex,
  index,
}: BottomButtonTrayProps) => {
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Handle clicking outside the dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDownloadMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="flex justify-between items-center bg-gray-200">
      {
        <div className="flex gap-1 p-1 pl-2">
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
      <div className="flex justify-end gap-2 p-1 border-t sticky bottom-0 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={onRegenerate}
          className="hover:bg-gray-300"
          disabled={isRegenerating}
        >
          <RefreshCcw
            className={cn("h-4 w-4", isRegenerating && "animate-spin")}
          />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCopy}
          className="hover:bg-gray-300"
        >
          <Copy className="h-4 w-4" />
        </Button>
        <div className="relative" ref={dropdownRef}>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDownloadMenu(!showDownloadMenu)}
            className="hover:bg-gray-300"
          >
            <Download className="h-4 w-4" />
          </Button>
          {showDownloadMenu && (
            <div className="absolute bottom-full right-0 mb-2 flex flex-col bg-white border rounded-md shadow-lg">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onDownload("pdf");
                  setShowDownloadMenu(false);
                }}
                className="whitespace-nowrap px-4"
              >
                Download PDF
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onDownload("md");
                  setShowDownloadMenu(false);
                }}
                className="whitespace-nowrap px-4"
              >
                Download Markdown
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ArtifactFrame = () => {
  const { sendMessage, createRegenerateSignalFrame } = useWebsocketContext();
  const {
    artifactObject,
    focus,
    setFocus,
    regeneratingTitle,
    setRegeneratingTitle,
  } = useArtifact();
  const prevArtifactCount = useRef(0);

  // Track artifact count changes
  useEffect(() => {
    if (!regeneratingTitle) return;

    const currentCount = artifactObject[regeneratingTitle]?.length || 0;
    if (currentCount > prevArtifactCount.current) {
      setRegeneratingTitle(null);
    }
    prevArtifactCount.current = currentCount;
  }, [artifactObject, regeneratingTitle]);

  const handleRegenerate = () => {
    if (!artifactObject[focus.title]?.length) return;
    if (focus.index === null) return;

    setRegeneratingTitle(focus.title);
    prevArtifactCount.current = artifactObject[focus.title].length;

    const regenerateFrame = createRegenerateSignalFrame(
      artifactObject[focus.title][focus.index]
    );
    sendMessage(regenerateFrame);
  };

  const handleCopyArtifact = async () => {
    if (!artifactObject[focus.title].length) return;
    if (focus.index === null) return;
    try {
      await navigator.clipboard.writeText(
        artifactObject[focus.title][focus.index].content || ""
      );
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleDownloadArtifact = async (format: "pdf" | "md") => {
    if (!artifactObject[focus.title].length || focus.index === null) return;

    const content = artifactObject[focus.title][focus.index].content || "";
    const title = artifactObject[focus.title][focus.index].title || "artifact";

    if (format === "md") {
      const blob = new Blob([content], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      return;
    }

    try {
      const { default: jsPDF } = await import("jspdf");
      const markdownIt = (await import("markdown-it")).default;
      const md = new markdownIt();

      // Convert markdown to plain text
      const plainText = md.render(content).replace(/<[^>]*>/g, "");

      // Create PDF
      const pdf = new jsPDF();
      const margin = 20;
      const pageWidth = pdf.internal.pageSize.getWidth() - 2 * margin;
      const pageHeight = pdf.internal.pageSize.getHeight();
      const lineHeight = 7;
      let cursorY = margin;

      // Add title
      pdf.setFontSize(16);
      pdf.text(title, margin, cursorY);
      cursorY += lineHeight * 2;

      // Add content with pagination
      pdf.setFontSize(12);
      const splitText = pdf.splitTextToSize(plainText, pageWidth);

      splitText.forEach((line: string) => {
        if (cursorY >= pageHeight - margin) {
          pdf.addPage();
          cursorY = margin;
        }
        pdf.text(line, margin, cursorY);
        cursorY += lineHeight;
      });

      pdf.save("artifact.pdf");
    } catch (err) {
      console.error("Failed to generate PDF:", err);
    }
  };

  const renderArtifactFrames = useCallback(() => {
    if (focus.index === null) return;
    return (
      <div className="w-full bg-white rounded-lg shadow-lg max-w-4xl mx-auto flex flex-col h-full">
        <TopButtonTray
          onClose={() => setFocus({ title: "", index: null })}
          title={artifactObject[focus.title][focus.index].title || ""}
        />

        {/* Content - scrollable */}
        <div className="flex-1 overflow-auto min-h-0">
          <div className="p-4">
            <Markdown
              remarkPlugins={[remarkGfm]}
              className="markdown-content break-words text-sm"
              components={components}
            >
              {artifactObject[focus.title][focus.index].content || ""}
            </Markdown>
          </div>
        </div>

        <BottomButtonTray
          numVersions={artifactObject[focus.title].length}
          setIndex={(index) => setFocus({ ...focus, index })}
          index={focus.index}
          onCopy={handleCopyArtifact}
          onDownload={handleDownloadArtifact}
          onRegenerate={handleRegenerate}
          isRegenerating={regeneratingTitle === focus.title}
        />
      </div>
    );
  }, [artifactObject, focus, setFocus, regeneratingTitle]);

  return <>{renderArtifactFrames()}</>;
};

export default ArtifactFrame;
