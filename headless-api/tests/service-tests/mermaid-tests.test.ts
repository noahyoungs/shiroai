import { axiosInstance } from './test-constants';
import fs from 'fs/promises';

const mermaidCode = `
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
`;

async function testMermaid() {
  const response = await axiosInstance.post('/mermaid', { code: mermaidCode });
  const { lightSvg, darkSvg } = response.data;

  await fs.writeFile('mermaid_light.svg', lightSvg);
  await fs.writeFile('mermaid_dark.svg', darkSvg);

  return { lightSvg, darkSvg };
}

async function testMermaidDimensions() {
  const response = await axiosInstance.post('/mermaid-dimensions', { code: mermaidCode });
  return response.data;
}

describe('Mermaid Tests', () => {
  it('should generate Mermaid SVGs', async () => {
    const { lightSvg, darkSvg } = await testMermaid();
    expect(lightSvg).toBeDefined();
    expect(darkSvg).toBeDefined();
  });

  it('should get Mermaid dimensions', async () => {
    const dimensions = await testMermaidDimensions();
    expect(dimensions.width).toBeDefined();
    expect(dimensions.height).toBeDefined();
  });
});