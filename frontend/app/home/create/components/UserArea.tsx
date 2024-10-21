"use client";
import InputArea from "./InputArea";

function Header() {
  return (
    <header className="bg-gray-300 rounded-sm text-center">
      Options to learn/configure/etc
    </header>
  );
}

function MessageContainer() {
  return (
    <div className="flex flex-col grow gap-2">
      <div className="bg-white p-2 rounded-lg">Message 1</div>
      <div className="bg-white p-2 rounded-lg">Message 2</div>
    </div>
  );
}

function UserArea() {
  return (
    <div className="flex flex-col gap-2 h-full">
      <Header />
      <MessageContainer />
      <InputArea />
    </div>
  );
}

export default UserArea;
