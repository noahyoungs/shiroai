export default {
  testMatch: [
    "**/tests/service-tests/**/*test.ts"
  ],
  moduleFileExtensions: [
    "js",
    "json",
    "ts"
  ],
  transform: {
    "^.+\\.ts$": "ts-jest"
  },
  testEnvironment: "node",
  // Add global timeout of 2 minutes (120000 ms)
  testTimeout: 1000 * 60 * 2,
};