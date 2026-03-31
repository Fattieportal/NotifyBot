// API configuration
// In Next.js client components, we need to use window.location to determine the API URL
// because process.env is not available in client-side code after build

export function getApiUrl(): string {
  // Check if we're in the browser
  if (typeof window !== 'undefined') {
    // In production, use the environment variable set at build time
    // In Vercel, this will be injected during build
    const envApiUrl = process.env.NEXT_PUBLIC_API_URL
    
    if (envApiUrl) {
      // Remove trailing slash
      return envApiUrl.replace(/\/$/, '')
    }
    
    // Fallback: if on localhost, use localhost:8000, otherwise assume backend is on same domain
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:8000'
    }
    
    // For production without env var, you'd need to manually set this
    return 'https://notify-bot-94oj.vercel.app'
  }
  
  // Server-side fallback (shouldn't be used in client components)
  return process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000'
}

export const API_URL = getApiUrl()
