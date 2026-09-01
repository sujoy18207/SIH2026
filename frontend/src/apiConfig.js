// Robust API Base URL supporting localhost, 127.0.0.1, custom ports & proxy
export const API_BASE_URL = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.port === '5173' ||
  window.location.port === '3000'
)
  ? 'http://localhost:8000'
  : '';
