"use client";

import { User } from "firebase/auth";
import { createContext, ReactNode, useState } from "react";
import { useFirebaseAuth } from "../hooks/useFirebaseAuth";

type AuthContextType = {
  user: User | null;
  loading: boolean;
};

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const { user, isLoading } = useFirebaseAuth();
  return (
    <AuthContext.Provider value={{ user: user, loading: isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
