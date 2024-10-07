import { ProviderType } from "@/types/auth";
import {
  GithubAuthProvider,
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  User,
} from "firebase/auth";
import {
  getServerSideuser,
  updateAuthCookie,
  verifyToken,
} from "../auth/action";
import auth from "../lib/firebase/firebaseClient";
import { useEffect, useState } from "react";
import clientLogger from "../lib/clientLogger";
import { useRouter } from "next/navigation";

export const useFirebaseAuth = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  const signIn = async (provider: ProviderType) => {
    setIsLoading(true);
    const authProvider =
      provider === "google"
        ? new GoogleAuthProvider()
        : new GithubAuthProvider();

    try {
      const { user } = await signInWithPopup(auth, authProvider);
      // clientLogger.debug("provider: ", provider, user, providerId);

      // get the id token, decode it from the server endpoint and set it as a cookie
      const token = await user.getIdToken();
      const decodedToken = await verifyToken(token);
      await updateAuthCookie(token);
      clientLogger.debug("decoded token: ", decodedToken);
      router.push("/home");
      return decodedToken;
    } catch (error) {
      clientLogger.error("Error during singing in: ", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    setIsLoading(true);
    try {
      // Uncomment the below line to simulate a slow network
      // await new Promise((resolve) => setTimeout(resolve, 5000));
      await auth.signOut();
      await updateAuthCookie(null);
    } catch (error) {
      clientLogger.error("Error during signing out: ", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    clientLogger.debug("useFirebase triggered");
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      clientLogger.debug("onAuthStateChanged triggered");
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
            clientLogger.debug(
              "firebase user found"
              // , firebaseUser
            );
            // clientLogger.debug("server user: ", serverUser);
          } else {
            await signOut();
            setUser(null);
          }
        } catch (error) {
          clientLogger.error("Error verifying user: ", error);
          await signOut();
          setUser(null);
        }
      } else {
        setUser(null);
        await updateAuthCookie(null);
      }
      setIsLoading(false);
    });
    return unsubscribe;
  }, []);

  return { user, isLoading, signIn, signOut };
};
