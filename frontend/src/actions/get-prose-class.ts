import axios from 'axios';
import { auth } from "@/auth";

const BASE_URL = process.env.HEADLESS_API_URL;
const DISABLE_SSL_VERIFY = process.env.DISABLE_SSL_VERIFY === 'true';

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  httpsAgent: DISABLE_SSL_VERIFY ? new (require('https').Agent)({ rejectUnauthorized: false }) : undefined
});

export async function getProseClass(markdown: string, title: string): Promise<string> {
  const session = await auth();
  const userId = session?.user?.id;

  if (!userId) {
    throw new Error("User is not authenticated. Database calls should not be made.");
  }

  const INTERNAL_API_KEY = process.env.HEADLESS_API_INTERNAL_KEY;

  if (!INTERNAL_API_KEY) {
    throw new Error("Internal API key is not set");
  }

  if (!markdown) {
    throw new Error("Markdown is required to determine prose class");
  }

  if (typeof markdown !== "string") {
    throw new Error(`Markdown must be a string, received ${typeof markdown}`);
  }

  if (!title) {
    throw new Error("Title is required to determine prose class");
  }

  const maxRetries = 3;
  let attempt = 0;

  while (attempt < maxRetries) {
    try {
      // Use the axiosInstance instead of axios directly
      const response = await axiosInstance.post('/prose-class', 
        { markdown, title },
        {
          headers: {
            'x-api-key': INTERNAL_API_KEY,
            'x-user-id': userId
          }
        }
      );
      const { proseClass } = response.data;

      console.log("Prose class:", proseClass);
      return proseClass;
    } catch (error: any) {
      attempt++;
      const delay = Math.pow(2, attempt) * 500; // Exponential backoff
      console.error(`Attempt ${attempt} failed: ${error.message}. Retrying in ${delay / 1000} seconds...`);

      if (attempt >= maxRetries) {
        throw new Error(`Failed to determine prose class after ${maxRetries} attempts. Error: ${error.response ? error.response.data : error.message}, markdown: ${markdown}`);
      }

      // Wait for the delay before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // This line should never be reached
  throw new Error("Unexpected error: retry loop exited unexpectedly.");
}
