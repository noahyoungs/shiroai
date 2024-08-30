import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { splitMarkdown } from '../../src/utils/split-markdown';

const BASE_URL = 'https://meetshiro.com:3003';
const IGNORE_SSL = true;
const HEADLESS_API_INTERNAL_KEY = process.env.HEADLESS_API_INTERNAL_KEY;

const jsonDataPath = path.join(__dirname, 'markdown-split-results.json');
const jsonData = JSON.parse(fs.readFileSync(jsonDataPath, 'utf-8'));

// Create an instance of Axios with or without SSL verification

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'x-api-key': HEADLESS_API_INTERNAL_KEY,
  },
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});

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