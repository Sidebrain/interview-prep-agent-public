"use server";

import "server-only";

import { cookies } from "next/headers";

const verifyToken = async (token: string) => {
  console.log("Backend URL", process.env.BACKEND_URL);
  // creating a request object
  const request = {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
  // making the actual request
  const response = await fetch(
    process.env.BACKEND_URL + "/auth/verify_token",
    request
  );

  if (!response.ok) {
    throw new Error("Failed to verify token");
  }

  return await response.json();
};

const getServerSideuser = async () => {
  const token = cookies().get("auth_token")?.value;

  if (!token) {
    return null;
  }
  try {
    return await verifyToken(token);
  } catch (error) {
    console.error("Error getting server side user: ", error);
    return null;
  }
};

const updateAuthCookie = async (token: string | null) => {
  if (token) {
    cookies().set("auth_token", token, {
      httpOnly: true,
      sameSite: "strict",
      secure: true,
    });
  } else {
    cookies().delete("auth_token");
  }
};

export { getServerSideuser, updateAuthCookie, verifyToken };
