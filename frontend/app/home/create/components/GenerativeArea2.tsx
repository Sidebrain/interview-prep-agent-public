"use client";
import React, { useCallback } from "react";
import { useArtifact } from "@/context/ArtefactContext";
import Markdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";

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
const ArtefactFrame = () => {
  const { artifactText } = useArtifact();
  const renderArtefactFrame = useCallback(
    (artefactText: string | null) => {
      if (!artefactText) return null;
      return (
        <div className="w-full bg-gray-100 h-full flex flex-col items-center overflow-scroll">
          <Markdown
            remarkPlugins={[remarkGfm]}
            className="markdown-content break-words text-sm p-4"
            components={components}
          >
            {artefactText}
          </Markdown>
        </div>
      );
    },
    [artifactText]
  );
  return <>{artifactText && renderArtefactFrame(artifactText)}</>;
};

const GenerativeArea2 = () => {
  return (
    <div className="w-full bg-gray-100 h-full flex flex-col items-center overflow-scroll">
      <ArtefactFrame />
    </div>
  );
};

export default GenerativeArea2;
