const axios = require('axios');
const fs = require('fs').promises;

const BASE_URL = 'https://meetshiro.com:3003';

// Test data
const mermaidCode = `
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
`;

const markdownText = `
# Slide Title

This is a sample markdown text for testing the prose class determination.
`;

const invalidMermaidCode = `
graph TD;
  A-->B
  A-->C;
  B->D;
  C-->D;
`;

async function testMermaid() {
  try {
    const response = await axios.post(`${BASE_URL}/mermaid`, { code: mermaidCode });
    const { lightSvg, darkSvg } = response.data;

    await fs.writeFile('tests/mermaid_light.svg', lightSvg);
    await fs.writeFile('tests/mermaid_dark.svg', darkSvg);

    console.log('Mermaid SVGs saved to files.');
  } catch (error) {
    console.error('Mermaid Error:', error.response ? error.response.data : error.message);
  }
}

async function testMermaidDimensions() {
  try {
    const response = await axios.post(`${BASE_URL}/mermaid-dimensions`, { code: mermaidCode });
    console.log('Mermaid Dimensions:', response.data);
  } catch (error) {
    console.error('Mermaid Dimensions Error:', error.response ? error.response.data : error.message);
  }
}

async function testProseClass() {
  try {
    const response = await axios.post(`${BASE_URL}/prose-class`, { markdown: markdownText });
    console.log('Prose Class:', response.data.proseClass);
  } catch (error) {
    console.error('Prose Class Error:', error.response ? error.response.data : error.message);
  }
}

async function testValidateMermaid() {
  try {
    const validResponse = await axios.post(`${BASE_URL}/validate-mermaid`, { diagram: mermaidCode });
    console.log('Valid Mermaid Diagram:', validResponse.data);

    const invalidResponse = await axios.post(`${BASE_URL}/validate-mermaid`, { diagram: invalidMermaidCode });
    console.log('Invalid Mermaid Diagram:', invalidResponse.data);
  } catch (error) {
    console.error('Validate Mermaid Error:', error.response ? error.response.data : error.message);
  }
}

async function runTests() {
  await testMermaid();
  await testMermaidDimensions();
  await testProseClass();
  await testValidateMermaid();
}

runTests();
