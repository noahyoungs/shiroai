import axios from 'axios';

const BASE_URL = process.env.HEADLESS_API_URL;
const DISABLE_SSL_VERIFY = process.env.DISABLE_SSL_VERIFY === 'true';

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  httpsAgent: DISABLE_SSL_VERIFY ? new (require('https').Agent)({ rejectUnauthorized: false }) : undefined
});

export async function getProseClass(markdown: string, title: string): Promise<string> {

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
      // Send the markdown and title to the new service
      const response = await axios.post(`${BASE_URL}/prose-class`, { markdown, title });
      const { proseClass } = response.data;

      console.log("Prose class:", proseClass);
      return proseClass;
    } catch (error) {
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
