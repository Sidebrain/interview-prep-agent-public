import { create } from "zustand";
import { WebsocketFrameType, createMessage } from "../types";

interface InterviewState {
  messages: WebsocketFrameType[];
  addMessage: (message: Parameters<typeof createMessage>[0]) => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  messages: [
    createMessage({
      content: "# Message Types Demo\n\nHere are examples of different message types we support:",
      role: "assistant",
      title: "Welcome",
    }),
    createMessage({
      content: "📝 **Text Message**\nThis is a simple text message with markdown support including:\n- Bullet points\n- *Italics*\n- **Bold text**\n- `Inline code`",
      role: "assistant",
      title: "Text Formatting",
    }),
    createMessage({
      content: "🖼️ **Image Example**\nHere's a high-quality workspace image:",
      role: "assistant",
      title: "Image Demo",
      media: [
        {
          type: "image",
          url: "https://images.unsplash.com/photo-1542831371-29b0f74f9713",
          title: "Clean Workspace Setup",
          width: 1920,
          height: 1080,
          aspectRatio: 16/9
        }
      ]
    }),
    createMessage({
      content: "🎥 **Video Example**\nA sample video demonstration:",
      role: "assistant",
      title: "Video Demo",
      media: [
        {
          type: "video",
          title: "Coding Tutorial",
          thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324a6cee",
          duration: 245
        }
      ]
    }),
    createMessage({
      content: "🎵 **Audio Example**\nVoice recording sample:",
      role: "assistant",
      title: "Audio Demo",
      media: [
        {
          type: "audio",
          title: "Interview Response",
          duration: 35,
          mimeType: "audio/mp3"
        }
      ]
    }),
    createMessage({
      content: "💻 **Code Example**\nHere's a TypeScript code sample:",
      role: "assistant",
      title: "Code Demo",
      media: [
        {
          type: "code",
          language: "typescript",
          code: `interface User {\n  id: string;\n  name: string;\n  email: string;\n}\n\nfunction greetUser(user: User): string {\n  return \`Hello, \${user.name}! Welcome back.\`;\n}`
        }
      ]
    }),
    createMessage({
      content: "📎 **File Attachment**\nHere's a document for review:",
      role: "assistant",
      title: "File Demo",
      media: [
        {
          type: "file",
          title: "Technical_Specification.pdf",
          size: 1024 * 1024 * 2.5 // 2.5MB
        }
      ]
    }),
    createMessage({
      content: "🔗 **Link Example**\nUseful resource:",
      role: "assistant",
      title: "Link Demo",
      media: [
        {
          type: "link",
          title: "Web Development Documentation",
          url: "https://developer.mozilla.org"
        }
      ]
    })
  ],
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, createMessage(message)],
    })),
}));