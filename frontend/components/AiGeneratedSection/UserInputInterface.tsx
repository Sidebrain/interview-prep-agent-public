"use client";
import { forwardRef, useEffect } from "react";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";

type HTMLTextAreaElementProps = {
  inputValue: string;
  onInputChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  maxHeight: number;
};

const UserInputInterface = forwardRef<
  HTMLTextAreaElement,
  HTMLTextAreaElementProps
>(({ inputValue, onInputChange, maxHeight, onKeyDown, onSubmit }, ref) => {
  //
  function adjustTextareaHeight() {
    if (ref && typeof ref !== "function" && ref.current) {
      ref.current.style.height = "auto";
      const newHeight = Math.min(ref.current.scrollHeight, maxHeight);
      ref.current.style.height = `${newHeight}px`;
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    onInputChange(e.target.value);
    adjustTextareaHeight();
  }

  useEffect(adjustTextareaHeight, [inputValue, maxHeight]);

  return (
    <div className="bg-white p-2">
      <form onSubmit={onSubmit} className="flex">
        <Textarea
          ref={ref}
          value={inputValue}
          onKeyDown={onKeyDown}
          onChange={handleInputChange}
          placeholder="Type a message..."
          className="flex-grow p-2 border rounded-lg resize-none mr-2"
          style={{ maxHeight: `${maxHeight}px` }}
          rows={1}
        />
        <Button type="submit" className="self-end">
          Send
        </Button>
      </form>
    </div>
  );
});

export default UserInputInterface;
