"use client";

import { useContext } from "react";
import { AuthContext } from "@/app/context/AuthContext";
import { ProviderType } from "@/types/auth";
import clientLogger from "@/app/lib/clientLogger";
import { Button } from "@/components/ui/button";
import { Icons } from "@/components/icons";
// import { useRouter } from "next/navigation";

const AuthButtons = () => {
  const { signIn, signOut, isLoading, user } = useContext(AuthContext);
  // const router = useRouter();

  const handleSignIn = async (provider: ProviderType) => {
    try {
      signIn(provider);
      // router.push("/home");
    } catch (error) {
      clientLogger.error("Error during signing in: ", error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      clientLogger.error("Error during signing out: ", error);
    }
  };

  return (
    <div className="flex gap-4 rounded-md p-4 justify-center">
      <Button
        type="button"
        variant={"outline"}
        disabled={isLoading}
        onClick={() => handleSignIn("google")}
      >
        {isLoading ? (
          <Icons.spinner className="mr-2 h-4 w-4" />
        ) : (
          <Icons.google className="mr-2 h-4 w-4" />
        )}
        Google
      </Button>
      <Button variant={"outline"} onClick={() => handleSignIn("github")}>
        <Icons.gitHub className="mr-2 h-4 w-4" /> Github
      </Button>
      {user && <Button onClick={() => handleSignOut()}>Sign Out</Button>}
    </div>
  );
};

export default AuthButtons;
