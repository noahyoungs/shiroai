import { axiosInstance, TEST_PRESENTATION_ID } from './test-constants';

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
    const { s3Key } = await testGeneratePdf(TEST_PRESENTATION_ID);
    expect(s3Key).toBeDefined();
    expect(s3Key).toMatch(new RegExp(`^${TEST_PRESENTATION_ID}/export/pdf/.+\.pdf$`));
  });
});