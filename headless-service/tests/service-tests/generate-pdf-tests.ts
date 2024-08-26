import axios from 'axios';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;

// Create an instance of Axios with or without SSL verification
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});

async function testGeneratePdf(presentationId: string) {
  const response = await axiosInstance.post(`/generate-pdf/${presentationId}/pdf`, {
    theme: "dark",
    footnotes: true
  });
  return response.data;
}

describe('Generate PDF Tests', () => {
  // Set a 30-second timeout for the tests in this suite
  jest.setTimeout(30000);

  it('should generate a PDF for the given presentation ID', async () => {
    const presentationId = '0190ca6b-c656-7a64-aa10-ad79716eca2f';
    const { s3Key } = await testGeneratePdf(presentationId);
    expect(s3Key).toBeDefined();
    expect(s3Key).toBe('0190ca6b-c656-7a64-aa10-ad79716eca2f/The_Future_of_Electric_Vehicles.pdf');
  });
});
