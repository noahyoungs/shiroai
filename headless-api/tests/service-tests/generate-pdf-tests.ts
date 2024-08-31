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

async function testGeneratePdf(presentationId: string) {
  const response = await axiosInstance.post(`/generate-pdf/${presentationId}/pdf`, {
    theme: "light",
    footnotes: true
  });
  return response.data;
}

describe('Generate PDF Tests', () => {
  jest.setTimeout(30000);

  it('should generate a PDF for the given presentation ID', async () => {
    const presentationId = '0191984f-980e-7227-900a-7076afc01d46';
    const { s3Key } = await testGeneratePdf(presentationId);
    expect(s3Key).toBeDefined();
    expect(s3Key).toBe('0191984f-980e-7227-900a-7076afc01d46/export/pdf/Effective_Strategies_for_Weight_Loss.pdf');
  });
});