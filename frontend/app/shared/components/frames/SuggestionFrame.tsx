import { useState } from 'react';
import {
  ThoughtSchema,
  WebsocketFrame,
} from "@/types/ScalableWebsocketTypes";

const SuggestionFrame = ({
  websocketFrame,
}: {
  websocketFrame: WebsocketFrame;
}) => {
  const [copiedSection, setCopiedSection] = useState<'sample' | 'options' | null>(null);
  
  const content = websocketFrame.frame.content;
  if (content === null) {
    return null;
  }
  const { success, data } = ThoughtSchema.safeParse(JSON.parse(content));

  console.log("SuggestionFrame:", {
    content,
    success,
    data,
  });

  if (!success || data === undefined) {
    return null;
  }

  const handleCopyToClipboard = (text: string, section: 'sample' | 'options') => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000); // Reset after 2 seconds
      console.log("Text copied to clipboard:", text);
    }).catch(err => {
      console.error("Could not copy text: ", err);
    });
  };

  return (
    <div className="bg-white border border-gray-300 rounded-lg p-5 shadow-sm">
      <div className="mb-5">
        <h3 className="text-gray-800 text-lg font-semibold mb-3">Sample Answer</h3>
        <div
          className="relative bg-gray-100 border border-gray-200 rounded-md p-4 text-gray-700 text-sm leading-relaxed hover:bg-gray-200 transition duration-200 cursor-pointer"
          onClick={() => handleCopyToClipboard(data.sampleAnswer, 'sample')}
        >
          {copiedSection === 'sample' && (
            <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-md text-xs animate-fade-out">
              Copied!
            </div>
          )}
          {data.sampleAnswer}
        </div>
      </div>
      
      <div className="mt-5">
        <h3 className="text-gray-800 text-lg font-semibold mb-3">Options</h3>
        <div
          className="relative bg-gray-100 border border-gray-200 rounded-md p-4 text-gray-700 text-sm leading-relaxed hover:bg-gray-200 transition duration-200 cursor-pointer"
          onClick={() => handleCopyToClipboard(data.options, 'options')}
        >
          {copiedSection === 'options' && (
            <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-md text-xs animate-fade-out">
              Copied!
            </div>
          )}
          {data.options}
        </div>
      </div>
    </div>
  );
};

export default SuggestionFrame;
