import React from 'react';
import { ShieldCheck, UserCheck, RefreshCw, Layers, ShieldAlert, Building2, Cpu, FileSpreadsheet } from 'lucide-react';

export default function Header({ persona, setPersona, activeTab, setActiveTab, onTriggerAnalytics, isRefreshing, onOpenCopilot }) {
  return (
    <header>
      {/* 1. Tricolor Top Accent Strip */}
      <div className="tricolor-bar" />

      {/* 2. Top Utility & Accessibility Bar */}
      <div className="top-utility-bar">
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>भारत सरकार | Government of India</span>
          <span>•</span>
          <span>सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय | MoSPI</span>
        </div>
        <div className="utility-links">
          <span>Font Size:</span>
          <button className="font-resizer-btn">A-</button>
          <button className="font-resizer-btn">A</button>
          <button className="font-resizer-btn">A+</button>
          <span>|</span>
          <span style={{ fontWeight: 600, color: '#fff' }}>English / हिंदी</span>
        </div>
      </div>

      {/* 3. Main GoI Branding Header */}
      <div className="goi-header">
        <div className="goi-brand-left">
          {/* Ashoka Stambh National Emblem SVG */}
          <svg className="emblem-icon" viewBox="0 0 100 100" fill="#002147">
            <path d="M50 5 L55 25 L75 25 L60 38 L65 58 L50 45 L35 58 L40 38 L25 25 L45 25 Z" fill="#d97706" />
            <circle cx="50" cy="65" r="18" fill="none" stroke="#002147" strokeWidth="4" />
            <path d="M50 47 L50 83 M32 65 L68 65 M37 52 L63 78 M37 78 L63 52" stroke="#002147" strokeWidth="2" />
            <rect x="20" y="86" width="60" height="8" rx="2" fill="#002147" />
          </svg>

          <div>
            <div className="goi-title-hi">सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय</div>
            <div className="goi-title-en">MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION</div>
            <div className="sub-title">MPLADS eSAKSHI Portal — AI Risk Intelligence & Decision Support Layer</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Persona Switcher Dropdown */}
          <div style={{
            background: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '4px',
            padding: '0.35rem 0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <UserCheck size={16} color="#002147" />
            <span style={{ fontSize: '0.78rem', color: '#475569', fontWeight: 600 }}>Persona Access:</span>
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                fontWeight: 700,
                color: '#002147',
                fontSize: '0.825rem',
                cursor: 'pointer'
              }}
            >
              <option value="Ministry">Ministry / MoSPI National Officer</option>
              <option value="State">State Nodal Authority (SNA)</option>
              <option value="District">District Collector / Authority</option>
              <option value="MP">Member of Parliament (MP)</option>
            </select>
          </div>

          <button
            onClick={onTriggerAnalytics}
            disabled={isRefreshing}
            className="btn-goi-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
            {isRefreshing ? 'Re-Running AI Pipeline...' : 'Re-Run Analytics'}
          </button>
        </div>
      </div>

      {/* 4. Official GoI Navbar */}
      <nav className="goi-navbar">
        <div className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <ShieldAlert size={16} color="#FF9933" />
            Risk Intelligence & Priority Review Feed
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'agencies' ? 'active' : ''}`}
            onClick={() => setActiveTab('agencies')}
          >
            <Building2 size={16} color="#FF9933" />
            Implementing Agency Performance Matrix
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={onOpenCopilot}
            className="btn-goi-saffron"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <Cpu size={16} /> Ask AI Copilot (सक्षम AI)
          </button>
        </div>
      </nav>

      {/* 5. Official Ticker Bar */}
      <div className="marquee-bar">
        <span style={{ background: '#d97706', color: '#fff', padding: '0.1rem 0.5rem', borderRadius: '3px', fontSize: '0.7rem', fontWeight: 800 }}>
          NOTICE
        </span>
        <span>
          eSAKSHI Portal AI Decision-Support Monitoring System — Currently analyzing 10,000+ sanctioned MPLADS works across 10 States & 30 Districts for cost overruns, delays, and duplicates.
        </span>
      </div>
    </header>
  );
}
