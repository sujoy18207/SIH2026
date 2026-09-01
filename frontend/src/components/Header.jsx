import React from 'react';
import { Home, LayoutDashboard, UserPlus, ShieldAlert, Building2, Lock, UserCheck, RefreshCw, Sparkles, MapPin } from 'lucide-react';
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
    <header style={{ position: 'sticky', top: 0, zIndex: 50, background: '#ffffff' }}>
      {/* 1. Tricolor Top Accent Line */}
      <div className="tricolor-bar" />

      {/* 2. Top Utility & Accessibility Bar */}
      <div className="top-utility-bar">
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <span>भारत सरकार • Government of India</span>
          <span>|</span>
          <span>सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय • MoSPI</span>
        </div>
        <div className="utility-links">
          <span>Font:</span>
          <button className="font-resizer-btn">A-</button>
          <button className="font-resizer-btn">A</button>
          <button className="font-resizer-btn">A+</button>
          <span>|</span>
          <span style={{ fontWeight: 600, color: '#f8fafc' }}>English / हिंदी</span>
        </div>
      </div>

      {/* 3. Main eSAKSHI Brand Header */}
      <div className="esakshi-header">
        <div className="esakshi-brand-left" style={{ cursor: 'pointer' }} onClick={() => setActiveTab('home')}>
          <AshokaStambhaLogo size={46} color="#0f2744" showMotto={true} />

          <div style={{ borderLeft: '1.5px solid #e2e8f0', paddingLeft: '1rem' }}>
            <div className="esakshi-title-hi">सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय</div>
            <div className="esakshi-title-en">MINISTRY OF STATISTICS AND PROGRAMME IMPLEMENTATION</div>
            <div className="esakshi-subtitle">
              <span>MPLADS e-SAKSHI</span>
              <span>•</span>
              <span style={{ color: '#0284c7' }}>AI Anomaly & Risk Intelligence Platform (PS-102)</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Persona Access Switcher */}
          <div style={{
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '6px',
            padding: '0.35rem 0.65rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <UserCheck size={15} color="#0d9488" />
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                fontWeight: 600,
                color: '#0f2744',
                fontSize: '0.8rem',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="Ministry">Ministry / MoSPI Officer</option>
              <option value="State">State Nodal Authority (SNA)</option>
              <option value="District">District Authority</option>
              <option value="MP">Member of Parliament</option>
            </select>
          </div>

          <button
            onClick={onTriggerAnalytics}
            disabled={isRefreshing}
            className="btn-esakshi-outline"
            title="Re-run Unsupervised AI Pipeline & Risk Fusion"
          >
            <RefreshCw size={13} className={isRefreshing ? 'spin' : ''} />
            {isRefreshing ? 'Analyzing...' : 'Re-Run AI'}
          </button>
        </div>
      </div>

      {/* 4. Streamlined Clean Navigation Bar */}
      <nav className="esakshi-navbar">
        <div className="esakshi-nav-tabs">
          <button
            className={`esakshi-nav-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            <Home size={16} />
            Home
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <ShieldAlert size={16} />
            Dashboard & Risk Feed
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            <MapPin size={16} />
            Geographic Risk Map
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'agencies' ? 'active' : ''}`}
            onClick={() => setActiveTab('agencies')}
          >
            <Building2 size={16} />
            Agency Risk Matrix
          </button>

          <button
            className={`esakshi-nav-btn ${activeTab === 'mps' ? 'active' : ''}`}
            onClick={() => setActiveTab('mps')}
          >
            <LayoutDashboard size={16} />
            MP Allocation Limits
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <button
            onClick={onOpenCopilot}
            style={{
              background: '#f0fdfa',
              border: '1px solid #ccfbf1',
              color: '#0f766e',
              padding: '0.4rem 0.85rem',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.15s ease'
            }}
          >
            <Sparkles size={14} color="#0d9488" />
            AI Copilot
          </button>

          <button
            onClick={onOpenCitizenRequest}
            className="btn-esakshi-outline"
            style={{ borderRadius: '20px', fontSize: '0.8rem', padding: '0.4rem 0.85rem' }}
          >
            <UserPlus size={14} />
            Citizen Portal
          </button>

          <button
            onClick={onOpenLogin}
            className="btn-esakshi-teal"
            style={{ borderRadius: '20px', fontSize: '0.8rem', padding: '0.4rem 1rem' }}
          >
            <Lock size={13} />
            {loggedInUser ? loggedInUser.name.split(' ')[0] : 'Officer Login'}
          </button>
        </div>
      </nav>
    </header>
  );
}
