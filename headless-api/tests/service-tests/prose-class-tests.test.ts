import { axiosInstance } from './test-constants';

const markdownText = `
# Slide Title

This is a sample markdown text for testing the prose class determination.
`;

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