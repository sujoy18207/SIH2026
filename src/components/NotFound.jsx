import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="not-found-container">
      <div className="not-found-card">
        <h1 className="error-code">404</h1>
        <h2 className="error-title">Page Not Found</h2>
        <p className="error-description">
          The page you are looking for doesn't exist or is under construction.
        </p>
        <button className="back-btn" onClick={() => navigate('/dashboard')}>
          Return to Home
        </button>
      </div>
    </div>
  );
}