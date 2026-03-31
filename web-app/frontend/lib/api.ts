// Backend API op Vercel — via NEXT_PUBLIC_API_URL env var overschrijfbaar
const envApiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '')

export const API_URL =
  envApiUrl ||
  (typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://notify-bot-api.vercel.app')
