module.exports = {
  testMatch: [
    "**/tests/service-tests/**/*.ts"
  ],
  moduleFileExtensions: [
    "js",
    "json",
    "ts"
  ],
  transform: {
    "^.+\\.ts$": "ts-jest"
  },
  testEnvironment: "node"
};
