import crypto from "crypto";
import globalLogger from "./logger";

export function createSignedUrlSuffix(
  policy: any,
  privateKey: string,
  keyPairId: string
): string {

  if (typeof privateKey !== 'string' || !privateKey.trim().startsWith('-----BEGIN PRIVATE KEY-----') || !privateKey.trim().endsWith('-----END PRIVATE KEY-----')) {
    const errorMessage = 'Invalid private key: must be a non-empty string in the proper format starting with -----BEGIN PRIVATE KEY----- and ending with -----END PRIVATE KEY-----';
    globalLogger.error(errorMessage);
    globalLogger.debug(privateKey);
    throw new Error(errorMessage);
  }


  const policyString = JSON.stringify(policy);
  const base64Policy = Buffer.from(policyString)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/=/g, "_")
    .replace(/\//g, "~");

  // Convert the privateKey string to a Buffer
  const privateKeyBuffer = Buffer.from(privateKey, 'utf-8');

  const sign = crypto.createSign("RSA-SHA1");
  sign.update(policyString);
  const signature = sign
    .sign(privateKeyBuffer, "base64")
    .replace(/\+/g, "-")
    .replace(/=/g, "_")
    .replace(/\//g, "~");

  return `?Policy=${base64Policy}&Signature=${signature}&Key-Pair-Id=${keyPairId}`;
}
