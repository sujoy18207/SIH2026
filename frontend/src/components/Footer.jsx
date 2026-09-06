import React from 'react';

export default function Footer() {
  return (
    <footer className="app-footer">
      <div>
        <strong style={{ color: '#0f172a', letterSpacing: '0.5px' }}>MoSPI RISK INTELLIGENCE</strong>
        <span style={{ margin: '0 0.5rem', color: '#cbd5e1' }}>|</span>
        <span>© 2024 Ministry of Statistics and Programme Implementation (MoSPI). Data Integrity: 100% | eSAKSHI Schema Verified</span>
      </div>

      <div className="footer-links">
        <a href="#privacy" className="footer-link">Data Privacy</a>
        <a href="#terms" className="footer-link">Terms of Service</a>
        <a href="#status" className="footer-link">API Status</a>
        <a href="#governance" className="footer-link">Governance Policy</a>
      </div>
    </footer>
  );
}
