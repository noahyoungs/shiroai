import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();
import axios from 'axios';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;
const HEADLESS_API_INTERNAL_KEY = process.env.HEADLESS_API_INTERNAL_KEY;

const markdownText = `
# Slide Title

This is a sample markdown text for testing the prose class determination.
`;

// Create an instance of Axios with or without SSL verification
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'x-api-key': HEADLESS_API_INTERNAL_KEY,
  },
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});

async function testProseClass() {
  const response = await axiosInstance.post('/prose-class', { markdown: markdownText, title: "Test Title" });
  return response.data.proseClass;
}

describe('Prose Class Tests', () => {
  it('should determine prose class', async () => {
    const proseClass = await testProseClass();
    expect(proseClass).toBeDefined();
  });
});