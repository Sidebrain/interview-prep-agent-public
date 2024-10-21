"use client";
import { useEffect, useRef, useState } from "react";
import InputArea from "./InputArea";
import MessageContainer from "./MessageContainer";

function Header() {
  return (
    <header className="bg-gray-300 rounded-sm text-center">
      Options to learn/configure/etc
    </header>
  );
}

function UserArea() {
  const [maxTextareaHeight, setMaxTextareaHeight] = useState(0);
  return (
    <div className="flex flex-col gap-2 h-full">
      <Header />
      <MessageContainer setMaxTextareaHeight={setMaxTextareaHeight} />
      <InputArea maxTextareaHeight={maxTextareaHeight} />
    </div>
  );
}

export default UserArea;
