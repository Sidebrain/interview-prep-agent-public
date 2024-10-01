import { initializeApp, apps, credential, auth } from "firebase-admin";

const firebaseConfig = {
  credential: {
    projectId: process.env.FIREBASE_PROJECT_ID,
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
    privateKey: process.env.FIREBASE_PRIVATE_KEY,
  },
};

if (!apps.length) {
  initializeApp({ credential: credential.cert(firebaseConfig.credential) });
}

export const adminAuth = auth();