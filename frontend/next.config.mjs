/** @type {import('next').NextConfig} */
const nextConfig = {
    
    reactStrictMode: false,
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: 'ai-presenter-2-sources-bucket.s3.us-west-2.amazonaws.com',
          port: '',
        },
      ],
    },
  };
  
  export default nextConfig;
