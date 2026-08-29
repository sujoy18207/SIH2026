import React from 'react';
import { Home, Info, LayoutDashboard, UserPlus, ShieldAlert, FileText, Video, ArrowRight, Lock } from 'lucide-react';

export default function HeroLanding({ onNavigateTab, onOpenCitizenRequest, onOpenLogin, onOpenCopilot }) {
  return (
    <div style={{ position: 'relative', width: '100%', overflow: 'hidden', background: '#f8fafc' }}>
      {/* Parliament Aerial Hero Section */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          minHeight: '520px',
          backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.45), rgba(15, 23, 42, 0.65)), url(/parliament_hero_bg.png)`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          justify: 'space-between'
        }}
      >
        {/* Top Floating Glassmorphic Header */}
        <div style={{
          padding: '1.25rem 2.5rem',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          background: 'rgba(0, 0, 0, 0.25)',
          backdropFilter: 'blur(8px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.15)'
        }}>
          {/* Left Emblem Branding */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <svg width="42" height="42" viewBox="0 0 100 100" fill="#ffffff">
              <path d="M50 5 L55 25 L75 25 L60 38 L65 58 L50 45 L35 58 L40 38 L25 25 L45 25 Z" fill="#FF9933" />
              <circle cx="50" cy="65" r="18" fill="none" stroke="#ffffff" strokeWidth="4" />
              <path d="M50 47 L50 83 M32 65 L68 65 M37 52 L63 78 M37 78 L63 52" stroke="#ffffff" strokeWidth="2" />
              <rect x="20" y="86" width="60" height="8" rx="2" fill="#ffffff" />
            </svg>
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f1f5f9', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Government of India
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#ffffff' }}>
                Ministry of Statistics and Programme Implementation
              </div>
              <div style={{ fontSize: '0.78rem', color: '#38bdf8', fontWeight: 700 }}>
                Members of Parliament Local Area Development Scheme
              </div>
            </div>
          </div>

          {/* Right Navigation Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              onClick={() => onNavigateTab('home')}
              style={{
                padding: '0.45rem 1rem',
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                borderRadius: '20px',
                color: '#ffffff',
                fontSize: '0.85rem',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Home
            </button>

            <button
              onClick={() => onNavigateTab('alerts')}
              style={{
                padding: '0.45rem 1rem',
                background: 'rgba(255, 255, 255, 0.12)',
                border: 'none',
                borderRadius: '20px',
                color: '#ffffff',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Dashboard
            </button>

            <button
              onClick={onOpenCitizenRequest}
              style={{
                padding: '0.45rem 1rem',
                background: 'rgba(255, 255, 255, 0.12)',
                border: 'none',
                borderRadius: '20px',
                color: '#ffffff',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Citizen Request
            </button>

            <button
              onClick={() => onNavigateTab('alerts')}
              style={{
                padding: '0.45rem 1rem',
                background: '#0284c7',
                border: 'none',
                borderRadius: '20px',
                color: '#ffffff',
                fontSize: '0.85rem',
                fontWeight: 700,
                cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
              }}
            >
              🛡️ AI Risk Platform (PS-102)
            </button>

            <button
              onClick={onOpenLogin}
              style={{
                padding: '0.45rem 1.4rem',
                background: '#ffffff',
                border: 'none',
                borderRadius: '20px',
                color: '#002147',
                fontSize: '0.85rem',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
              }}
            >
              Login
            </button>
          </div>
        </div>

        {/* Center Hero Banner Title */}
        <div style={{ padding: '4rem 3rem 2rem 3rem', maxWidth: '850px' }}>
          <h1 style={{ fontSize: '2.8rem', fontWeight: 800, leading: 1.1, marginBottom: '0.8rem', color: '#ffffff', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
            <span style={{ color: '#38bdf8' }}>MPLADS:</span> From Local Priorities to National Development
          </h1>
          <p style={{ fontSize: '1.15rem', color: '#f1f5f9', fontWeight: 500, textShadow: '0 1px 4px rgba(0,0,0,0.5)', maxWidth: '680px' }}>
            eSAKSHI — SAnsad sadasya sthaniya KSHetra vIkas yojana.<br />
            AI-Powered Anomaly, Fraud & Inefficiency Monitoring Ecosystem.
          </p>
          <div style={{ width: '60px', height: '4px', background: '#38bdf8', marginTop: '1.2rem', borderRadius: '2px' }} />
        </div>

        {/* Tricolor Wave Bottom Graphic Overlay */}
        <div style={{ width: '100%', overflow: 'hidden', lineHeight: 0, marginTop: 'auto' }}>
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" style={{ position: 'relative', display: 'block', width: 'calc(100% + 1.3px)', height: '80px' }}>
            <path d="M0,0 C150,90 350,-40 500,40 C650,120 900,10 1200,60 L1200,120 L0,120 Z" fill="#FF9933" opacity="0.6"></path>
            <path d="M0,20 C200,100 450,0 700,70 C950,140 1100,20 1200,80 L1200,120 L0,120 Z" fill="#138808" opacity="0.4"></path>
            <path d="M0,40 C300,110 600,10 900,90 C1050,130 1150,50 1200,100 L1200,120 L0,120 Z" fill="#ffffff"></path>
          </svg>
        </div>
      </div>

      {/* Quick Action Navigation Grid */}
      <div style={{ maxWidth: '1200px', margin: '-2.5rem auto 3rem auto', padding: '0 1.5rem', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
          
          <div
            onClick={() => onNavigateTab('alerts')}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderTop: '4px solid #0091ff',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 4px 15px rgba(0,0,0,0.06)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              transition: 'transform 0.2s'
            }}
          >
            <div style={{ background: '#e0f2fe', width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <LayoutDashboard size={26} color="#0091ff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#002147' }}>Public Dashboard</div>
              <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Sanctions & Expenditure Stats</div>
            </div>
          </div>

          <div
            onClick={() => onNavigateTab('alerts')}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderTop: '4px solid #c53030',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 4px 15px rgba(0,0,0,0.06)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem'
            }}
          >
            <div style={{ background: '#fff5f5', width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldAlert size={26} color="#c53030" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#002147' }}>AI Anomaly Platform</div>
              <div style={{ fontSize: '0.78rem', color: '#9b2c2c', fontWeight: 600 }}>PS-102 Risk Intelligence</div>
            </div>
          </div>

          <div
            onClick={onOpenCitizenRequest}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderTop: '4px solid #16a34a',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 4px 15px rgba(0,0,0,0.06)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem'
            }}
          >
            <div style={{ background: '#f0fdf4', width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <UserPlus size={26} color="#16a34a" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#002147' }}>Citizen Request</div>
              <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Propose Local Need to MP</div>
            </div>
          </div>

          <div
            onClick={onOpenLogin}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderTop: '4px solid #d97706',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 4px 15px rgba(0,0,0,0.06)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem'
            }}
          >
            <div style={{ background: '#fffbebfb', width: '54px', height: '54px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Lock size={26} color="#d97706" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#002147' }}>Officer Login</div>
              <div style={{ fontSize: '0.78rem', color: '#64748b' }}>MoSPI / District Portal</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
