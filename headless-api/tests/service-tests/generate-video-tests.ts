import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

import axios from 'axios';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;
const HEADLESS_API_INTERNAL_KEY = process.env.HEADLESS_API_INTERNAL_KEY;

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

async function testGenerateVideo(presentationId: string) {
  const response = await axiosInstance.post(`/generate-mp4/${presentationId}/mp4`, {
    outputResolution: "1920x1080",
    theme: "light",
    footnotes: false,
  });
  return response.data;
}

describe('Generate Video Tests', () => {
  jest.setTimeout(15 * 60 * 1000);  // Set timeout for 15 mins

  it('should generate a video file (MP4) for the given presentation ID', async () => {
    const presentationId = '0191a820-edbd-7686-97c7-826543d56b76'; // Example presentation ID
    const { videoS3Key } = await testGenerateVideo(presentationId);
    
    // Check that the response contains a valid S3 key for the generated video
    expect(videoS3Key).toBeDefined();
    expect(typeof videoS3Key).toBe('string');
    expect(videoS3Key).toMatch(new RegExp(`^s3://.+/export/mp4/final-video\\.mp4$`));
  });
});