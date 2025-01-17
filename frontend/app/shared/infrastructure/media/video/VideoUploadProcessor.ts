import clientLogger from "@/app/lib/clientLogger";
import { BaseMediaProcessor, SignedUrlResponse } from "../types";

export class VideoUploadProcessor extends BaseMediaProcessor<string> {
    private getSignedUrl: () => Promise<SignedUrlResponse>;

    constructor(getSignedUrl: () => Promise<SignedUrlResponse>) {
        super();
        this.getSignedUrl = getSignedUrl;
    }

    public process = async (media: Blob | null): Promise<string | null> => {
        if (!this.validateMedia(media)) {
            return null;
        }
        try {
            const signedUrl = await this.getSignedUrl();
            clientLogger.debug("Uploading video", {
                signedUrl: signedUrl,
                mediaType: signedUrl.storage_filename,
            });
            const response = await fetch(signedUrl.url, {
                method: "PUT",
                body: media,
                headers: {
                    "content-type": "video/webm",
                    "x-goog-content-length-range": "0,1000000000",
                },
            });
            if (!response.ok) {
                throw new Error(`Failed to upload video: ${response.statusText}`);
            }
            return signedUrl.storage_filename;
        } catch (error) {
            clientLogger.error("Failed to upload video", {
                error: error,
            });
            throw new Error(`Failed to upload video: ${error}`);
        }
    }
}