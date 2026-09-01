import React from 'react';
import { 
  Search, 
  Bell, 
  Globe, 
  User, 
  Sparkles,
  Menu
} from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  onOpenCopilot,
  onOpenLogin,
  loggedInUser,
  searchTerm,
  setSearchTerm,
  isSidebarOpen,
  setIsSidebarOpen
}) {
  return (
    <header className="top-header">
      {/* Brand Title & Hamburger Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button 
          className="icon-btn"
          onClick={() => setIsSidebarOpen && setIsSidebarOpen(!isSidebarOpen)}
          title={isSidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        >
          <Menu size={20} />
        </button>

        <div className="top-brand" onClick={() => setActiveTab('home')}>
          <span>MoSPI Risk Intelligence</span>
        </div>
      </div>

      {/* Global Search Input */}
      <div className="top-search-wrap">
        <Search size={16} className="top-search-icon" />
        <input 
          type="text" 
          placeholder="Search works, regions..." 
          className="top-search-input"
          value={searchTerm || ''}
          onChange={(e) => setSearchTerm && setSearchTerm(e.target.value)}
        />
      </div>

      {/* Main Navigation Links (Matching Core Sections) */}
      <div className="top-nav-links">
        <button
          className={`top-nav-link ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          Overview
        </button>

        <button
          className={`top-nav-link ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Risk Dashboard
        </button>

        <button
          className={`top-nav-link ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => setActiveTab('map')}
        >
          Risk Map
        </button>

        <button
          className={`top-nav-link ${activeTab === 'agencies' ? 'active' : ''}`}
          onClick={() => setActiveTab('agencies')}
        >
          Agency Matrix
        </button>

        <button
          className={`top-nav-link ${activeTab === 'mps' ? 'active' : ''}`}
          onClick={() => setActiveTab('mps')}
        >
          MP Allocation
        </button>

        <button
          className="top-nav-link"
          onClick={onOpenCopilot}
          style={{ color: '#0d9488' }}
        >
          <Sparkles size={15} />
          AI Copilot
        </button>
      </div>

      {/* Right Icons: Notifications, Language, Profile */}
      <div className="top-actions">
        <button className="icon-btn" title="Notifications" onClick={() => setActiveTab('alerts')}>
          <Bell size={18} />
          <span className="badge-dot" />
        </button>

        <button className="icon-btn" title="Language Switcher (EN / HI)">
          <Globe size={18} />
        </button>

        <button className="icon-btn" title="User Profile / Login" onClick={onOpenLogin}>
          <User size={18} />
        </button>
      </div>
    </header>
  );
}
