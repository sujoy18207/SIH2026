// API Base URL helper supporting local dev & Vercel deployment
export const API_BASE_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : '';
