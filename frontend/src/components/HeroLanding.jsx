import React from 'react';
import { LayoutDashboard, UserPlus, ShieldAlert, Lock, ArrowRight, Sparkles, CheckCircle2, Search, Database, MapPin } from 'lucide-react';

export default function HeroLanding({ onNavigateTab, onOpenCitizenRequest, onOpenLogin, onOpenCopilot }) {
  return (
    <div style={{ position: 'relative', width: '100%', background: '#f8fafc' }}>
      
      {/* High-Impact Hero Banner */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          minHeight: '420px',
          backgroundImage: `linear-gradient(135deg, rgba(15, 39, 68, 0.92), rgba(10, 25, 47, 0.96)), url(/parliament_hero_bg.png)`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '3.5rem 2.5rem 5rem 2.5rem'
        }}
      >
        <div style={{ maxWidth: '1100px', margin: '0 auto', width: '100%' }}>
          
          {/* Subtle Top Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.85rem',
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: '#38bdf8',
            marginBottom: '1.25rem'
          }}>
            <Sparkles size={14} />
            Smart India Hackathon 2026 • Problem Statement PS-102
          </div>

          {/* Main Title */}
          <h1 style={{
            fontSize: '2.75rem',
            fontWeight: 800,
            lineHeight: 1.15,
            marginBottom: '1rem',
            letterSpacing: '-0.5px'
          }}>
            AI-Powered <span style={{ color: '#38bdf8' }}>MPLADS</span> Anomaly & Risk Intelligence
          </h1>

          <p style={{
            fontSize: '1.1rem',
            color: '#cbd5e1',
            fontWeight: 400,
            maxWidth: '720px',
            lineHeight: 1.6,
            marginBottom: '2rem'
          }}>
            Real-time multi-signal monitoring, explainable 0–100 risk prioritization, expenditure anomaly detection, and duplicate work prevention for the eSAKSHI ecosystem.
          </p>

          {/* CTA Buttons */}
          <div style={{ display: 'flex', gap: '0.85rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              onClick={() => onNavigateTab('alerts')}
              style={{
                background: '#0d9488',
                color: '#ffffff',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 14px rgba(13, 148, 136, 0.35)',
                transition: 'all 0.15s ease'
              }}
            >
              <LayoutDashboard size={18} />
              Open Risk Dashboard
            </button>

            <button
              onClick={() => onNavigateTab('map')}
              style={{
                background: '#dc2626',
                color: '#ffffff',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 14px rgba(220, 38, 38, 0.35)'
              }}
            >
              <MapPin size={18} />
              Geographic Risk Map
            </button>

            <button
              onClick={onOpenCopilot}
              style={{
                background: 'rgba(255, 255, 255, 0.12)',
                color: '#ffffff',
                border: '1px solid rgba(255, 255, 255, 0.25)',
                backdropFilter: 'blur(8px)',
                padding: '0.75rem 1.3rem',
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Sparkles size={18} color="#38bdf8" />
              Ask AI Copilot
            </button>

            <button
              onClick={onOpenCitizenRequest}
              style={{
                background: 'transparent',
                color: '#e2e8f0',
                border: '1px solid rgba(255, 255, 255, 0.18)',
                padding: '0.75rem 1.2rem',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <UserPlus size={16} />
              Citizen Portal
            </button>
          </div>

        </div>
      </div>

      {/* Modern Floating Action Cards */}
      <div style={{ maxWidth: '1100px', margin: '-2.5rem auto 3.5rem auto', padding: '0 1.5rem', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
          
          {/* Card 1: Risk Monitoring */}
          <div
            onClick={() => onNavigateTab('alerts')}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ background: '#fef2f2', width: '48px', height: '48px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldAlert size={24} color="#dc2626" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f2744' }}>Anomaly Intelligence</div>
                <div style={{ fontSize: '0.78rem', color: '#dc2626', fontWeight: 600 }}>128,081 Projects Monitored</div>
              </div>
            </div>
            <div style={{ fontSize: '0.825rem', color: '#64748b', lineHeight: 1.5 }}>
              Unsupervised Isolation Forest + Deterministic Compliance Rule checks with explainable scores.
            </div>
          </div>

          {/* Card 2: Agency Risk */}
          <div
            onClick={() => onNavigateTab('agencies')}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ background: '#f0fdfa', width: '48px', height: '48px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Database size={24} color="#0d9488" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f2744' }}>Agency Risk Matrix</div>
                <div style={{ fontSize: '0.78rem', color: '#0d9488', fontWeight: 600 }}>21,367 Contractors Profiled</div>
              </div>
            </div>
            <div style={{ fontSize: '0.825rem', color: '#64748b', lineHeight: 1.5 }}>
              Track stall rates, cost overruns, and historical anomaly concentration by implementing agency.
            </div>
          </div>

          {/* Card 3: MP Allocations */}
          <div
            onClick={() => onNavigateTab('mps')}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ background: '#f0f9ff', width: '48px', height: '48px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <LayoutDashboard size={24} color="#0284c7" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f2744' }}>MP Allocation Limits</div>
                <div style={{ fontSize: '0.78rem', color: '#0284c7', fontWeight: 600 }}>544 Parliamentary Limits</div>
              </div>
            </div>
            <div style={{ fontSize: '0.825rem', color: '#64748b', lineHeight: 1.5 }}>
              Monitor sanctioned vs recommended limits, constituency expenditure trends, and fund utilization.
            </div>
          </div>

          {/* Card 4: Officer Login */}
          <div
            onClick={onOpenLogin}
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ background: '#fffbeb', width: '48px', height: '48px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Lock size={24} color="#d97706" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f2744' }}>Authorized Review</div>
                <div style={{ fontSize: '0.78rem', color: '#d97706', fontWeight: 600 }}>MoSPI / District Portal</div>
              </div>
            </div>
            <div style={{ fontSize: '0.825rem', color: '#64748b', lineHeight: 1.5 }}>
              Submit official officer verification remarks, desk audit feedback, and field inspection requests.
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
