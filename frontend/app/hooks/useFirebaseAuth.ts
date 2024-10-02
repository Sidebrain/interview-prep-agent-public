import { ProviderType } from "@/types/auth";
import {
  GithubAuthProvider,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import { updateAuthCookie, verifyToken } from "../auth/action";
import auth from "../lib/firebase/firebaseClient";

export const useFirebaseAuth = () => {
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

  return { signIn, signOut };
};
