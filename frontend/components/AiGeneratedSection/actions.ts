"use server";

import serverLogger from "@/app/lib/serverLogger";

export async function transcribeAudioChunks(formdata: FormData) {
  serverLogger.debug("formadata received: ", formdata);
  const audioChunks = formdata.get("file") as File;
  if (!audioChunks) {
    throw new Error("No audio chunks found");
  }

  const response = await fetch(
    process.env.BACKEND_URL + "/api/v1/audio/transcribe",
    {
      method: "POST",
      body: formdata,
    }
  );

  return { transcription: await response.json() };
}
