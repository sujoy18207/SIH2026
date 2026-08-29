import React from 'react';
import { Home, LayoutDashboard, UserPlus, ShieldAlert, Building2, Cpu, Lock, UserCheck, RefreshCw } from 'lucide-react';
import AshokaStambhaLogo from './AshokaStambhaLogo';

export default function Header({
  persona,
  setPersona,
  activeTab,
  setActiveTab,
  onTriggerAnalytics,
  isRefreshing,
  onOpenCopilot,
  onOpenCitizenRequest,
  onOpenLogin,
  loggedInUser
}) {
  return (
    <header>
      {/* 1. Tricolor Top Accent Line */}
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

      {/* 3. Main eSAKSHI Header with Ashoka Stambha Emblem */}
      <div className="esakshi-header">
        <div className="esakshi-brand-left">
          {/* Authentic Ashoka Stambha State Emblem of India Logo */}
          <AshokaStambhaLogo size={52} color="#002147" showMotto={true} />

          <div style={{ borderLeft: '2px solid #e2e8f0', paddingLeft: '1rem' }}>
            <div className="esakshi-title-hi">सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय</div>
            <div className="esakshi-title-en">MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION</div>
            <div className="esakshi-subtitle">MPLADS e-SAKSHI Portal • AI Anomaly, Fraud & Inefficiency Platform (PS-102)</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {/* Persona Access Switcher */}
          <div style={{
            background: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '4px',
            padding: '0.35rem 0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <UserCheck size={16} color="var(--esakshi-teal)" />
            <span style={{ fontSize: '0.78rem', color: '#475569', fontWeight: 600 }}>Persona:</span>
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
            className="btn-esakshi-outline"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
            {isRefreshing ? 'Re-Running AI...' : 'Re-Run Analytics'}
          </button>
        </div>
      </div>

      {/* 4. Official eSAKSHI Navigation Bar */}
      <nav className="esakshi-navbar">
        <div className="esakshi-nav-tabs">
          <button
            className={`esakshi-nav-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            <Home size={16} color="var(--esakshi-teal)" />
            Home
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <ShieldAlert size={16} color="var(--esakshi-teal)" />
            AI Risk Intelligence & Priority Review Feed
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'agencies' ? 'active' : ''}`}
            onClick={() => setActiveTab('agencies')}
          >
            <Building2 size={16} color="var(--esakshi-teal)" />
            Executing Agency Risk Matrix
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
          <button
            onClick={onOpenCitizenRequest}
            className="btn-esakshi-teal"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <UserPlus size={16} /> Citizen Request Portal
          </button>

          <button
            onClick={onOpenCopilot}
            className="btn-esakshi-outline"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', borderColor: 'var(--goi-saffron)', color: '#b45309' }}
          >
            <Cpu size={16} /> Ask AI Copilot (सक्षम AI)
          </button>

          <button
            onClick={onOpenLogin}
            className="btn-esakshi-outline"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', borderColor: '#002147', color: '#002147', fontWeight: 800 }}
          >
            <Lock size={15} /> {loggedInUser ? `Officer: ${loggedInUser}` : 'Login'}
          </button>
        </div>
      </nav>

      {/* 5. Official Announcement Ticker Bar */}
      <div className="esakshi-marquee">
        <span style={{ background: 'var(--esakshi-teal)', color: '#fff', padding: '0.1rem 0.5rem', borderRadius: '3px', fontSize: '0.7rem', fontWeight: 800 }}>
          NOTICE
        </span>
        <span>
          Official eSAKSHI Portal AI Decision-Support Layer — Monitoring 10,000+ sanctioned MPLADS works across 10 States & 30 Districts for cost overruns, timeline delays, and spatial duplicate candidate works.
        </span>
      </div>
    </header>
  );
}
