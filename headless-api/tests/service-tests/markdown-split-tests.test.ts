import { axiosInstance } from './test-constants';
import fs from 'fs';
import path from 'path';

const jsonDataPath = path.join(__dirname, 'markdown-split-results.json');
const jsonData = JSON.parse(fs.readFileSync(jsonDataPath, 'utf-8'));

async function testMarkdownSplit(markdown: string) {
  const response = await axiosInstance.post('/markdown-split/split', { markdown });
  return response.data;
}

describe('Markdown Split Tests', () => {
  jsonData.forEach((data: any, index:number ) => {
    it(`should split markdown ${index + 1} correctly`, async () => {
      const { firstPart, secondPart } = await testMarkdownSplit(data.original);

      console.log(`Test Case ${index + 1}`);
      console.log('Original:', data.original);
      console.log('Expected First Part:', JSON.stringify(data.firstPart));
      console.log('Received First Part:', JSON.stringify(firstPart));
      console.log('Expected Second Part:', JSON.stringify(data.secondPart));
      console.log('Received Second Part:', JSON.stringify(secondPart));

      expect(firstPart.trim()).toEqual(data.firstPart.trim());
      expect(secondPart.trim()).toEqual(data.secondPart.trim());
    });
  });
});