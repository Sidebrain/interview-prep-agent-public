"use client";

// Import the functions you need from the SDKs you need
import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";
// import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBufKW_mn6PjJ0EOTdKNNewvmLZtDYo0rw",
  authDomain: "public-project-436308.firebaseapp.com",
  projectId: "public-project-436308",
  storageBucket: "public-project-436308.appspot.com",
  messagingSenderId: "853157660767",
  appId: "1:853157660767:web:9a9c0ed00ddc6317ca73ea",
  measurementId: "G-RKW2T14VN0",
};

// Initialize Firebase
const app =
  getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
// const analytics = getAnalytics(app);

export default auth;
