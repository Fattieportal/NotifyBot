// Backend draait op de VPS — via NEXT_PUBLIC_API_URL env var in Vercel
const envApiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '')

export const API_URL =
  envApiUrl ||
  (typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'http://65.21.145.110:8000')
