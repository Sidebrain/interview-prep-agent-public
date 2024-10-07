"use client";

import { createContext, ReactNode } from "react";
import { useFirebaseAuth } from "../hooks/useFirebaseAuth";
import { AuthContextType } from "@/types/auth";

export const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  signIn: () => {},
  signOut: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const { user, isLoading, signIn, signOut } = useFirebaseAuth();
  return (
    <AuthContext.Provider
      value={{
        user: user,
        isLoading: isLoading,
        signIn: signIn,
        signOut: signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
