"use client";

import { onAuthStateChanged, User } from "firebase/auth";
import { createContext, ReactNode, useEffect, useState } from "react";
import auth from "../lib/firebase/firebaseClient";
import { getServerSideuser, updateAuthCookie } from "../auth/action";
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
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { signOut } = useFirebaseAuth();
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // get fresh idtoken
          const token = await firebaseUser.getIdToken();
          // update the auth cookie on server
          await updateAuthCookie(token);
          // verify the token on server
          const serverUser = await getServerSideuser();
          if (serverUser) {
            setUser(firebaseUser);
            console.log("firebase user: ", firebaseUser);
            console.log("server user: ", serverUser);
          } else {
            await signOut();
            setUser(null);
          }
        } catch (error) {
          console.error("Error verifying user: ", error);
          await signOut();
          setUser(null);
        }
      } else {
        setUser(null);
        await updateAuthCookie(null);
      }
      setLoading(false);
    });
    return unsubscribe;
  }, []);
  return (
    <AuthContext.Provider value={{ user: user, loading: loading }}>
      {children}
    </AuthContext.Provider>
  );
};
