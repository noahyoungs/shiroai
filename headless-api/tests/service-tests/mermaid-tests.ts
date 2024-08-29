import axios from 'axios';
import fs from 'fs/promises';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;

const mermaidCode = `
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
`;

// Create an instance of Axios with or without SSL verification
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});

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
