import { Mic } from "lucide-react";

export function Header() {
  return (
    <header className="border-b bg-card sticky top-0 z-50">
      <div className="container flex h-14 items-center px-4 max-w-6xl mx-auto">
        <div className="flex items-center space-x-2">
          <Mic className="h-6 w-6" />
          <h1 className="font-semibold">AI Interview Assistant</h1>
        </div>
        <div className="ml-auto flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Technical Interview - Round 1</span>
        </div>
      </div>
    </header>
  );
}