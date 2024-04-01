// src/utils/hash_email.ts

import { createHash } from 'crypto';

export function hashEmail(email: string | undefined | null): string {
  if (!email) {
    throw new Error('Email is required');
  }
  const hash = createHash('sha256');
  hash.update(email);
  return hash.digest('hex');
}