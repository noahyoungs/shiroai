'use server'

import axios from 'axios';

export async function exportToPDF(presentationId: string, theme: 'dark' | 'light' | 'print', footnotes: boolean) {
  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_HEADLESS_API_PATH}/generate-pdf/${presentationId}/pdf`,
      { theme, footnotes },
      {
        headers: {
          'x-api-key': process.env.HEADLESS_API_INTERNAL_KEY,
        },
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