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

async function testGenerateJpgs(presentationId: string) {
  const response = await axiosInstance.post(`generate-jpg/${presentationId}/jpg`, {
    theme: "light",
    footnotes: true,
    resolution: "1920x1080"
  });
  return response.data;
}

describe('Generate JPGs Tests', () => {
  jest.setTimeout(60000);

  it('should generate a zip file of JPEGs for the given presentation ID', async () => {
    const presentationId = '0191984f-980e-7227-900a-7076afc01d46';
    const { s3Key } = await testGenerateJpgs(presentationId);
    
    // Check that the response contains a valid S3 key
    expect(s3Key).toBeDefined();
    expect(typeof s3Key).toBe('string');
    expect(s3Key).toMatch(new RegExp(`^${presentationId}/slides.zip$`));
  });
});