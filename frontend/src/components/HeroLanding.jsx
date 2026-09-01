import React from 'react';
import { 
  ArrowRight, 
  Map, 
  Sparkles, 
  Layers, 
  TrendingUp, 
  TrendingDown, 
  ShieldCheck, 
  Search, 
  Activity,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

export default function HeroLanding({ 
  onNavigateTab, 
  onOpenCitizenRequest, 
  onOpenCopilot,
  stats 
}) {
  const monitoredWorks = stats?.total_projects || 128081;
  const releasedExp = stats?.total_sanctioned_amount 
    ? (stats.total_sanctioned_amount / 10000000).toLocaleString('en-IN', { maximumFractionDigits: 2 })
    : '3,939.54';
  const priorityRisks = stats?.high_risk_count || 1620;

  return (
    <div style={{ width: '100%' }}>
      {/* 1. Hero Grid Section */}
      <div className="hero-grid">
        {/* Left Column Text & CTAs */}
        <div>
          <div className="sih-badge">
            <span className="sih-dot" />
            <span>SMART INDIA HACKATHON 2026 • PS-102</span>
          </div>

          <h1 className="hero-title">
            AI-Powered<br />
            MPLADS<br />
            <span className="teal-text">Risk Intelligence</span>
          </h1>

          <p className="hero-subtitle">
            Real-time multi-signal monitoring, explainable risk prioritization, 
            expenditure anomaly detection, and duplicate-work prevention for the eSAKSHI ecosystem.
          </p>

          <div className="hero-actions">
            <button className="btn-primary-dark" onClick={() => onNavigateTab('alerts')}>
              <span>Open Risk Dashboard</span>
              <ArrowRight size={16} />
            </button>

            <button className="btn-secondary-outline" onClick={() => onNavigateTab('map')}>
              <Map size={16} />
              <span>Explore Risk Map</span>
            </button>

            <button className="btn-teal-outline" onClick={onOpenCopilot}>
              <Sparkles size={16} />
              <span>Ask AI Copilot</span>
            </button>
          </div>
        </div>

        {/* Right Column Interactive Floating Map Visual */}
        <div className="hero-map-card" onClick={() => onNavigateTab('map')} style={{ cursor: 'pointer' }}>
          <div className="map-card-topbar">
            <span>Intelligence Dashboard</span>
            <span style={{ color: '#0d9488' }}>Live Satellite Sync</span>
          </div>

          <div className="map-canvas-wrap">
            {/* SVG India Map Silhouette with glowing radar pulses */}
            <svg viewBox="0 0 400 420" style={{ width: '100%', height: '100%' }}>
              <defs>
                <linearGradient id="mapGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#0d9488" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#0284c7" stopOpacity="0.4" />
                </linearGradient>
                <radialGradient id="radarPulse" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
                </radialGradient>
              </defs>

              {/* Simplified high-tech stylized India map paths */}
              <path
                d="M 180 30 L 210 50 L 230 70 L 220 90 L 260 110 L 290 120 L 320 110 L 340 130 L 320 160 L 280 170 L 270 190 L 290 220 L 260 250 L 230 310 L 200 370 L 190 380 L 180 340 L 160 290 L 140 240 L 110 200 L 120 160 L 140 130 L 170 110 L 160 60 Z"
                fill="url(#mapGradient)"
                opacity="0.25"
                stroke="#0d9488"
                strokeWidth="1.5"
              />

              {/* Grid lines */}
              <line x1="50" y1="100" x2="350" y2="100" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="50" y1="200" x2="350" y2="200" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="50" y1="300" x2="350" y2="300" stroke="#e2e8f0" strokeDasharray="3 3" />

              {/* Glowing Pulse Nodes */}
              <circle cx="210" cy="130" r="14" fill="url(#radarPulse)">
                <animate attributeName="r" values="6;22;6" dur="2.5s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2.5s" repeatCount="indefinite" />
              </circle>
              <circle cx="210" cy="130" r="4" fill="#ef4444" />

              <circle cx="180" cy="270" r="12" fill="#10b981" opacity="0.3">
                <animate attributeName="r" values="5;18;5" dur="3s" repeatCount="indefinite" />
              </circle>
              <circle cx="180" cy="270" r="4" fill="#10b981" />

              <circle cx="260" cy="220" r="10" fill="#0284c7" opacity="0.3" />
              <circle cx="260" cy="220" r="3" fill="#0284c7" />
            </svg>

            {/* Anomaly Callout Overlay (matching screenshot 1) */}
            <div className="map-callout-anomaly">
              <AlertTriangle size={16} color="#ef4444" />
              <div>
                <strong style={{ color: '#0f172a', display: 'block', fontSize: '0.75rem' }}>Anomaly Detected</strong>
                <span style={{ color: '#64748b', fontSize: '0.7rem' }}>Exp. mismatch</span>
              </div>
            </div>

            {/* Verified Sync Callout Overlay (matching screenshot 1) */}
            <div className="map-callout-sync">
              <CheckCircle2 size={16} color="#10b981" />
              <div>
                <strong style={{ color: '#0f172a', display: 'block', fontSize: '0.75rem' }}>Verified Sync</strong>
                <span style={{ color: '#64748b', fontSize: '0.7rem' }}>Node active</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. System Overview Metrics Section (Matching Screenshot 1) */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 className="section-heading">System Overview</h2>
        
        <div className="metrics-row">
          {/* Card 1: Monitored Works */}
          <div className="metric-card accent-navy">
            <div className="metric-header">
              <Layers size={16} />
              <span>Monitored Works</span>
            </div>
            <div className="metric-value">
              {Number(monitoredWorks).toLocaleString()}
            </div>
            <div className="metric-trend trend-up">
              <TrendingUp size={13} />
              <span>+8.4% (30d)</span>
            </div>
          </div>

          {/* Card 2: Released Exp. (Cr) */}
          <div className="metric-card accent-teal">
            <div className="metric-header">
              <Activity size={16} />
              <span>Released Exp. (Cr)</span>
            </div>
            <div className="metric-value">
              ₹{releasedExp}
            </div>
            <div className="metric-trend trend-up">
              <TrendingUp size={13} />
              <span>+3.2% (30d)</span>
            </div>
          </div>

          {/* Card 3: Priority Risks */}
          <div className="metric-card accent-amber">
            <div className="metric-header">
              <AlertTriangle size={16} />
              <span>Priority Risks</span>
            </div>
            <div className="metric-value">
              {Number(priorityRisks).toLocaleString()}
            </div>
            <div className="metric-trend trend-down">
              <TrendingDown size={13} />
              <span>-4.7% (Resolved)</span>
            </div>
          </div>

          {/* Card 4: Data Integrity (Dark Card with Shield Badge) */}
          <div className="metric-card card-dark">
            <div className="metric-header">
              <ShieldCheck size={16} color="#10b981" />
              <span>Data Integrity</span>
            </div>
            <div className="metric-value">
              <span>100%</span>
              <CheckCircle2 size={20} color="#10b981" />
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Index Standard Maintained
            </div>
          </div>
        </div>
      </div>

      {/* 3. Citizen Portal Access Section */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 className="section-heading">Citizen Portal Access</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
          <div 
            className="metric-card" 
            onClick={onOpenCitizenRequest}
            style={{ cursor: 'pointer', display: 'flex', gap: '1rem', alignItems: 'flex-start' }}
          >
            <div style={{ background: '#f1f5f9', padding: '0.75rem', borderRadius: '8px' }}>
              <Search size={22} color="#0d9488" />
            </div>
            <div>
              <strong style={{ fontSize: '0.95rem', color: '#0f172a', display: 'block', marginBottom: '0.25rem' }}>
                Search Local Works
              </strong>
              <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
                Search for local MPLADS works by state, district, or MP constituency to view transparency reports.
              </p>
            </div>
          </div>

          <div 
            className="metric-card" 
            onClick={onOpenCitizenRequest}
            style={{ cursor: 'pointer', display: 'flex', gap: '1rem', alignItems: 'flex-start' }}
          >
            <div style={{ background: '#f1f5f9', padding: '0.75rem', borderRadius: '8px' }}>
              <Activity size={22} color="#0284c7" />
            </div>
            <div>
              <strong style={{ fontSize: '0.95rem', color: '#0f172a', display: 'block', marginBottom: '0.25rem' }}>
                Track Work Status
              </strong>
              <p style={{ fontSize: '0.825rem', color: '#64748b' }}>
                Enter a work ID to see real-time status updates, fund utilization, and AI-assessed completion metrics.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
