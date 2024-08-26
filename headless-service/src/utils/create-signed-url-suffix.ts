import crypto from "crypto";

export function createSignedUrlSuffix(
  policy: any,
  privateKey: string,
  keyPairId: string
): string {
  const policyString = JSON.stringify(policy);
  const base64Policy = Buffer.from(policyString)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/=/g, "_")
    .replace(/\//g, "~");

  const sign = crypto.createSign("RSA-SHA1");
  sign.update(policyString);
  const signature = sign
    .sign(privateKey, "base64")
    .replace(/\+/g, "-")
    .replace(/=/g, "_")
    .replace(/\//g, "~");

  return `?Policy=${base64Policy}&Signature=${signature}&Key-Pair-Id=${keyPairId}`;
}
