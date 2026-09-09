// In development (Vite dev server), point to local FastAPI backend directly.
// In production (Docker / Nginx), use relative '' so Nginx reverse-proxies /api/ automatically.
export const API_BASE_URL = import.meta.env.DEV
  ? (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  : '';

