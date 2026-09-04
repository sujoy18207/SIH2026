import React from 'react';
import './ComingSoon.css';

export default function ComingSoon() {
  return (
    <div className="coming-soon-wrapper">
      <div className="glass-card">
        {/* Brand Header */}
        <div className="card-brand">BWU 404</div>

        {/* Center Content */}
        <div className="card-main">
          <p className="subtitle">UNDER CONSTRUCTION</p>
          <h1 className="title">COMING SOON</h1>

          {/* Rocket Progress Bar */}
          <div className="progress-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '58%' }}>
                <span className="train-icon">🚀</span>
              </div>
            </div>
            <span className="percentage">58%</span>
          </div>
        </div>

        {/* Footer Links */}
        <div className="card-footer">
          <div className="footer-contact">
            CONTACT : <a href="mailto:shankhodeepdas609@gmail.com">
                        shankhodeepdas609@gmail.com
                      </a>
          </div>
          <div className="footer-domain">Thank you for having patience</div>
          <div className="footer-socials">
            <a href="https://github.com/shankhodeep-das" target="_blank" rel="noopener noreferrer">Github</a>
            <a href="#instagram">Instagram</a>
            <a href="#twitter">Linked in</a>
          </div>
        </div>
      </div>
    </div>
  );
}