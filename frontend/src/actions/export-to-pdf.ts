// frontend/src/actions/export-to-pdf.ts
'use server'

import axios from 'axios';
import https from 'https';
import { auth } from "@/auth";
import { uuidv7 } from "uuidv7";

// Control SSL verification for development purposes
const DISABLE_SSL_VERIFICATION = process.env.NODE_ENV === 'development';

export async function exportToPDF(presentationId: string, theme: 'dark' | 'light' | 'print', footnotes: boolean) {
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
      `${process.env.HEADLESS_API_URL}/generate-pdf/${presentationId}/pdf`,
      { theme, footnotes },
      {
        headers: {
          'x-api-key': process.env.HEADLESS_API_INTERNAL_KEY,
          'x-user-id': userId,
        },
        httpsAgent, // Pass the custom HTTPS agent to axios if SSL verification is disabled
      }
    );

    const { s3Key } = response.data;
    const href = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${s3Key}`;
    return { success: true, href };
  } catch (error: any) {
    console.error("Failed to export PDF on server side:", error);
    return { success: false, error: error.message || "Unknown error occurred" };
  }
}