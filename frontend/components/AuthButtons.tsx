"use client";

import { Button } from "./ui/button";
import { useContext } from "react";
import { AuthContext } from "@/app/context/AuthContext";
import { ProviderType } from "@/types/auth";
import {
  GithubAuthProvider,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import auth from "@/app/lib/firebase/firebaseClient";
import { updateAuthCookie, verifyToken } from "@/app/auth/action";
import { cookies } from "next/headers";
import { useFirebaseAuth } from "@/app/hooks/useFirebaseAuth";
import { Icons } from "./icons";
import { Icon } from "lucide-react";

type AuthButtonsProps = {
  signIn: (provider: ProviderType) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthButtons = () => {
  const user = useContext(AuthContext);
  const { signIn, signOut, isLoading } = useFirebaseAuth();

  const handleSignIn = async (provider: ProviderType) => {
    try {
      signIn(provider);
    } catch (error) {
      console.error("Error during signing in: ", error);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error("Error during signing out: ", error);
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
      {user.user && <Button onClick={() => handleSignOut()}>Sign Out</Button>}
    </div>
  );
};

export default AuthButtons;
