/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ]
  },
  images: {
    domains: ['via.placeholder.com', 'marktplaats.nl', 'autoscout24.nl', 'mobile.de', 'kleinanzeigen.de'],
  },
}

module.exports = nextConfig
