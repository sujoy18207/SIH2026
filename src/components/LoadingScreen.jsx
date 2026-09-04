import React from 'react';
import './LoadingScreen.css';

export default function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loader-content">
        <span className="loader-icon">🪐</span>
        <div className="spinner"></div>
        <p className="loading-text">Loading the Platform...</p>
      </div>
    </div>
  );
}