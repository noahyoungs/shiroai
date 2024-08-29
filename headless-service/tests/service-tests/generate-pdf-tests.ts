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
    theme: "light",
    footnotes: true
  });
  return response.data;
}

describe('Generate PDF Tests', () => {
  // Set a 30-second timeout for the tests in this suite
  jest.setTimeout(30000);

  it('should generate a PDF for the given presentation ID', async () => {
    const presentationId = '0191984f-980e-7227-900a-7076afc01d46';
    const { s3Key } = await testGeneratePdf(presentationId);
    expect(s3Key).toBeDefined();
    expect(s3Key).toBe('0191984f-980e-7227-900a-7076afc01d46/Effective_Strategies_for_Weight_Loss.pdf');
  });
});
