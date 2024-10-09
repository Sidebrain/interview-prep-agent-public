"use client";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Icons } from "@/components/icons";
import clientLogger from "../lib/clientLogger";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { ModeToggle } from "@/components/ThemeSwitcher";

export default function Header({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const { signOut, isLoading } = useContext(AuthContext);
  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      clientLogger.error("Error during signing out: ", error);
    }
  };
  return (
    <div className="flex flex-col h-screen">
      <header className="bg-gray-200 w-full">
        <div className="flex gap-2 p-2 w-full justify-end items-center">
          <ModeToggle />
          <Button variant="outline">Account</Button>
          <Button variant="outline">Dashboard</Button>
          <Button
            variant="default"
            onClick={handleSignOut}
            disabled={isLoading}
          >
            {isLoading ? (
              <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              "Sign Out"
            )}
          </Button>
        </div>
      </header>
      <div className="flex h-full overflow-scroll">{children}</div>
      <footer className="bg-gray-200 w-full">
        <div className="flex gap-2 p-2 w-full text-sm justify-between">
          <Link href="/about" className="">
            About
          </Link>
          <Link href="/about">T&C</Link>
        </div>
      </footer>
    </div>
  );
}
