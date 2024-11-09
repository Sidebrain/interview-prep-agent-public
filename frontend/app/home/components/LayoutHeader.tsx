import { Icons } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

type LayoutHeaderProps = {
  isLoading: boolean;
  handleSignOut: () => void;
};

export default function LayoutHeader(props: LayoutHeaderProps) {
  const [isChangelogOpen, setIsChangelogOpen] = useState(false);
  const [changelogContent, setChangelogContent] = useState("");

  useEffect(() => {
    // Load the changelog content when component mounts
    fetch("/changeLog.md")
      .then((response) => response.text())
      .then((content) => setChangelogContent(content))
      .catch((error) => console.error("Error loading changelog:", error));
  }, []);

  return (
    <>
      <header className="bg-gray-200 w-full">
        <div className="flex gap-2 p-2 w-full justify-end items-center">
          <Button variant="outline" onClick={() => setIsChangelogOpen(true)}>
            Change Log
          </Button>
          <Button
            variant="default"
            onClick={props.handleSignOut}
            disabled={props.isLoading}
          >
            {props.isLoading ? (
              <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              "Sign Out"
            )}
          </Button>
        </div>
      </header>

      <Dialog open={isChangelogOpen} onOpenChange={setIsChangelogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Change Log</DialogTitle>
          </DialogHeader>
          <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-bold prose-h1:text-xl prose-h2:text-lg">
            <Markdown
              remarkPlugins={[remarkGfm]}
              className="markdown-content break-words "
            >
              {changelogContent}
            </Markdown>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
