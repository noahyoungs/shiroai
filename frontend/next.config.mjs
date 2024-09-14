import path from 'path';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  serverComponentsExternalPackages: ["pino", "pino-pretty"],
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@shared-utils': path.resolve(__dirname, '../shared_ts/utils'),
    };
    return config;
  },
};

export default nextConfig;