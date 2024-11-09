"use client";
import React, { useCallback, useEffect, useState } from "react";
import { useArtifact } from "@/context/ArtifactContext";
import Markdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { X, Copy, Download, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
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
    <div className="flex justify-between items-center bg-gray-200">
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
      <div className="flex justify-end gap-2 p-1 border-t sticky bottom-0 z-10">
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
  const { sendMessage, createRegenerateSignalFrame } = useWebsocketContext();
  const { artifactObject, focus, setFocus } = useArtifact();

  const handleRegenerate = () => {
    if (!artifactObject[focus.title].length) return;
    if (focus.index === null) return;
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

  const handleDownloadArtifact = async () => {
    if (!artifactObject[focus.title].length) return;
    if (focus.index === null) return;

    try {
      // Import browser-compatible PDF libraries
      const { default: jsPDF } = await import('jspdf');
      const { default: html2canvas } = await import('html2canvas');
      
      // Create a temporary div to render the markdown content
      const tempDiv = document.createElement('div');
      tempDiv.className = 'markdown-content';
      const markdownIt = (await import('markdown-it')).default;
      const md = new markdownIt();
      tempDiv.innerHTML = md.render(artifactObject[focus.title][focus.index].content || "");
      document.body.appendChild(tempDiv);

      // Convert the rendered content to canvas
      const canvas = await html2canvas(tempDiv);
      document.body.removeChild(tempDiv);

      // Create PDF
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'px',
        format: 'a4'
      });

      // Add the canvas as image to PDF
      const imgData = canvas.toDataURL('image/png');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);

      // Download the PDF
      pdf.save('artifact.pdf');

    } catch (err) {
      console.error("Failed to generate PDF:", err);
    }
  };

  const renderArtifactFrames = useCallback(() => {
    if (focus.index === null) return;
    return (
      <div className="w-full bg-white rounded-lg shadow-lg max-w-4xl mx-auto my-2 flex flex-col h-full">
        <TopButtonTray
          onClose={() => setFocus({ title: "", index: null })}
          title={artifactObject[focus.title][focus.index].title || ""}
        />

        {/* Content - scrollable */}
        <div className="flex-1 overflow-auto min-h-0">
          <div className="p-6">
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
        />
      </div>
    );
  }, [artifactObject, focus, setFocus]);

  return <>{renderArtifactFrames()}</>;
};

export default ArtifactFrame;
