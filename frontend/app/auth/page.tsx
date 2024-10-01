"use client";

import AuthButtons from "@/components/AuthButtons";
import { signIn, signOut } from "./action";

const AuthPage = () => {
  return (
    <>
      <AuthButtons signIn={signIn} signOut={signOut} />
    </>
  );
};

export default AuthPage;
