import React from 'react';
import { Home, ShieldAlert, Building2, Award, MapPin, Cpu, UserPlus, Lock, RefreshCw } from 'lucide-react';
import AshokaStambhaLogo from './AshokaStambhaLogo';

const NAV_TABS = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'alerts', label: 'Risk Dashboard', icon: ShieldAlert },
  { id: 'map', label: 'Risk Map', icon: MapPin },
  { id: 'agencies', label: 'Agencies', icon: Building2 },
  { id: 'mps', label: 'MP Allocations', icon: Award },
];

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
  loggedInUser,
}) {
  return (
    <header className="glass-navbar">
      {/* Brand block */}
      <div className="nav-brand">
        <div className="nav-brand-emblem">
          <AshokaStambhaLogo size={38} color="#173a67" showMotto={false} />
          <div>
            <div className="nav-brand-title">e-SAKSHI <span>AI</span></div>
            <div className="nav-brand-sub">MoSPI · MPLADS Risk Intelligence</div>
          </div>
        </div>
      </div>

      {/* Primary navigation (single line) */}
      <nav className="nav-tabs" aria-label="Primary">
        {NAV_TABS.map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              className={`nav-tab ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}
            >
              <Icon size={16} strokeWidth={2} />
              <span>{t.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Actions */}
      <div className="nav-actions">
        {/* Persona switcher */}
        <div className="persona-select">
          <select
            value={persona}
            onChange={(e) => setPersona(e.target.value)}
            aria-label="Select persona"
          >
            <option value="Ministry">Ministry Officer</option>
            <option value="State">State Authority</option>
            <option value="District">District Collector</option>
            <option value="MP">Member of Parliament</option>
          </select>
        </div>

        <button className="nav-action-btn ghost" onClick={onTriggerAnalytics} disabled={isRefreshing}>
          <RefreshCw size={15} className={isRefreshing ? 'spin' : ''} />
          <span>{isRefreshing ? 'Running' : 'Re-run'}</span>
        </button>

        <button className="nav-action-btn solid" onClick={onOpenCopilot}>
          <Cpu size={16} />
          <span>AI Copilot</span>
        </button>

        <button className="nav-action-btn ghost" onClick={onOpenCitizenRequest}>
          <UserPlus size={16} />
          <span>Citizen</span>
        </button>

        <button className="nav-action-btn ghost" onClick={onOpenLogin}>
          <Lock size={15} />
          <span>{loggedInUser ? `Officer` : 'Login'}</span>
        </button>
      </div>
    </header>
  );
}
