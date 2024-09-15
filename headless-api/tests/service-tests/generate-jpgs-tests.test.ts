import { axiosInstance, TEST_PRESENTATION_ID } from './test-constants';

async function testGenerateJpgs(presentationId: string) {
  const response = await axiosInstance.post(`generate-jpg/${presentationId}/jpg`, {
    theme: "light",
    footnotes: true,
    resolution: "1920x1080",
  });
  return response.data;
}

describe('Generate JPGs Tests', () => {
  jest.setTimeout(60000);

  it('should generate a zip file of JPEGs for the given presentation ID', async () => {
    const { s3Key } = await testGenerateJpgs(TEST_PRESENTATION_ID);
    
    expect(s3Key).toBeDefined();
    expect(typeof s3Key).toBe('string');
    expect(s3Key).toMatch(new RegExp(`^${TEST_PRESENTATION_ID}/export/jpg/[^/]+\.zip$`));
  });
});