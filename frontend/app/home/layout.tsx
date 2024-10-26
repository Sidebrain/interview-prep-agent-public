"use client";
import clientLogger from "../lib/clientLogger";
import { useContext } from "react";
import { AuthContext } from "@/context/AuthContext";
import LayoutHeader from "./components/LayoutHeader";
import LayoutFooter from "./components/LayoutFooter";

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
      <LayoutHeader
        isLoading={isLoading}
        handleSignOut={handleSignOut}
      ></LayoutHeader>

      <div className="flex h-full overflow-scroll">{children}</div>

      <LayoutFooter />
    </div>
  );
}
