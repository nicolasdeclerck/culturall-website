/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'http',
        hostname: 'minio',
      },
      {
        protocol: 'https',
        hostname: '*.nickorp.com',
      },
      {
        protocol: 'https',
        hostname: 'cultur-all.org',
      },
      {
        protocol: 'https',
        hostname: '*.cultur-all.org',
      },
    ],
  },
};

module.exports = nextConfig;
