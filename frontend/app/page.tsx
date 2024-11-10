"use client";
import { AuthContext } from "@/context/AuthContext";
import { useContext } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const { user } = useContext(AuthContext);
  const router = useRouter();

  if (user) {
    router.push("/home/create");
    return null;
  }
  return (
    <div className="font-[family-name:var(--font-geist-sans)] justify-center items-center flex h-screen">
      {/* <AuthButtons signIn={signIn} signOut={signOut} /> */}
      Loading...
    </div>
  );
}
