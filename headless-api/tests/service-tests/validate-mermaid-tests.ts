import axios from 'axios';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;

const mermaidCode = `
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
`;

const invalidMermaidCode = `
graph TD;
  A-->B
  A-->C;
  B->D;
  C-->D;
`;

// Create an instance of Axios with or without SSL verification
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});

async function testValidateMermaid(valid: boolean) {
  const diagram = valid ? mermaidCode : invalidMermaidCode;
  const response = await axiosInstance.post('/validate-mermaid', { diagram });
  return response.data;
}

describe('Validate Mermaid Tests', () => {
  it('should validate valid Mermaid diagram', async () => {
    const result = await testValidateMermaid(true);
    expect(result.valid).toBe(true);
  });

  it('should invalidate invalid Mermaid diagram', async () => {
    const result = await testValidateMermaid(false);
    expect(result.valid).toBe(false);
  });
});
