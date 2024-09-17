// frontend/src/actions/generate-video.ts
'use server'

import axios from 'axios';
import https from 'https';
import { auth } from "@/auth";

// Control SSL verification based on the environment variable DISABLE_SSL_VERIFY
const DISABLE_SSL_VERIFICATION = process.env.DISABLE_SSL_VERIFY === 'true';

export async function generateVideo(
  presentationID: string,
  resolution: '1280x720' | '1920x1080',
  theme: 'dark' | 'light' | 'print',
  footnotes: boolean,
  voice: 'Danielle' | 'Gregory' | 'Ruth'
) {
  // Create an HTTPS agent that ignores SSL certificate errors if SSL verification is disabled
  const httpsAgent = DISABLE_SSL_VERIFICATION ? new https.Agent({ rejectUnauthorized: false }) : undefined;

  // Fetch the session data using the auth function
  const session = await auth();

  // Check if the user object and user id are available in the session
  if (!session || !session.user || !session.user.id) {
    // Throw an error if the user is not authenticated
    throw new Error("User is not authenticated. Database calls should not be made.");
  }

  const userId = session.user.id;

  try {
    const response = await axios.post(
      `${process.env.HEADLESS_API_URL}/generate-mp4/${presentationID}/mp4`,
      { resolution, theme, footnotes, voice },
      {
        headers: {
          'x-api-key': process.env.HEADLESS_API_INTERNAL_KEY,
          'x-user-id': userId,
        },
        httpsAgent, // Pass the custom HTTPS agent to axios if SSL verification is disabled
      }
    );

    const { videoS3Key } = response.data;
    const href = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${videoS3Key}`;
    return { success: true, href };
  } catch (error: any) {
    console.error("Failed to generate video on server side:", error);

    // Check if the error response is available and contains a message
    if (error.response) {
      const status = error.response.status;
      const errorMessage = error.response.data; // Extract the error message from the response body

      console.error(`Error status: ${status}, message: ${errorMessage}`);
      return { success: false, error: errorMessage || "Unknown error occurred" };
    }

    // Return a generic error message if no specific error response is available
    return { success: false, error: error.message || "Unknown error occurred" };
  }
}
