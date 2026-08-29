import React from 'react';

export default function Footer() {
  return (
    <footer className="goi-footer">
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div>
          © Content Owned and Maintained by Ministry of Statistics and Programme Implementation (MoSPI), Government of India
        </div>
        <div>
          Designed & Developed by SIH 2026 Hackathon Team • Integrated with eSAKSHI Digital Ecosystem Reference Framework
        </div>
        <div style={{ fontSize: '0.72rem', color: '#6b7280', marginTop: '0.5rem' }}>
          Disclaimer: This system serves strictly as an AI Risk Intelligence & Decision Support Layer for authorized officials. It does not replace formal administrative procedures.
        </div>
      </div>
    </footer>
  );
}
