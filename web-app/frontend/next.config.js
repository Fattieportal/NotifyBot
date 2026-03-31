/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://localhost:8000/api/:path*'
          : '/api/:path*',
      },
    ]
  },
  images: {
    domains: ['via.placeholder.com', 'marktplaats.nl', 'autoscout24.nl', 'mobile.de', 'kleinanzeigen.de'],
  },
}

module.exports = nextConfig
