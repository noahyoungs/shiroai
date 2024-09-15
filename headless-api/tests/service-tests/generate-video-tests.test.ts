import { axiosInstance, TEST_PRESENTATION_ID } from './test-constants';

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
    const { videoS3Key } = await testGenerateVideo(TEST_PRESENTATION_ID);
    
    expect(videoS3Key).toBeDefined();
    expect(typeof videoS3Key).toBe('string');
    expect(videoS3Key).toMatch(new RegExp(`^s3://.+/export/mp4/final-video\\.mp4$`));
  });
});