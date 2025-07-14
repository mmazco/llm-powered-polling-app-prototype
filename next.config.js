/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://llm-powered-polling-app-prototype-production.up.railway.app/:path*',
      },
    ];
  },
};

module.exports = nextConfig; 