import { User } from "firebase/auth";

export type ProviderType = "google" | "github";

export type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  signIn: (provider: ProviderType) => void;
  signOut: () => void;
};
