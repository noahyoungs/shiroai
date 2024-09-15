import dotenv from 'dotenv';
dotenv.config();

export const BASE_URL = 'https://meetshiro.com:3003';
export const IGNORE_SSL = true;
export const HEADLESS_API_INTERNAL_KEY = process.env.HEADLESS_API_INTERNAL_KEY;
export const TEST_USER_ID = 'c8612330-8031-709a-7002-9ab7be191fc8';
export const TEST_PRESENTATION_ID = '0191f46a-e6d2-73d5-ae45-fb7d8480da97';

import axios from 'axios';

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'x-api-key': HEADLESS_API_INTERNAL_KEY,
    'x-user-id': TEST_USER_ID,
  },
  httpsAgent: new (require('https').Agent)({
    rejectUnauthorized: !IGNORE_SSL,
  }),
});