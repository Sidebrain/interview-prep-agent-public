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

type AuthButtonsProps = {
  signIn: (provider: ProviderType) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthButtons = () => {
  const user = useContext(AuthContext);

  const signIn = async (provider: ProviderType) => {
    const authProvider =
      provider === "google"
        ? new GoogleAuthProvider()
        : new GithubAuthProvider();

    try {
      const { user, providerId } = await signInWithPopup(auth, authProvider);
      console.log("provider: ", provider, user, providerId);

      // get the id token, decode it from the server endpoint and set it as a cookie
      const token = await user.getIdToken();
      const decodedToken = await verifyToken(token);
      await updateAuthCookie(token);
      console.log("decoded token: ", decodedToken);
      return decodedToken;
    } catch (error) {
      console.error("Error during singing in: ", error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await auth.signOut();
      await updateAuthCookie(null);
    } catch (error) {
      console.error("Error during signing out: ", error);
      throw error;
    }
  };

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
    <div className="flex gap-4 rounded-md bg-gray-100 p-4">
      <Button onClick={() => handleSignIn("google")}>
        Sign In With Google
      </Button>
      <Button onClick={() => handleSignIn("github")}>
        Sign In With Github
      </Button>
      {user.user && <Button onClick={() => handleSignOut()}>Sign Out</Button>}
    </div>
  );
};

export default AuthButtons;
