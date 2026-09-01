import React from 'react';
import { 
  Home,
  ShieldAlert, 
  MapPin, 
  Building2, 
  LayoutDashboard, 
  Sparkles, 
  UserPlus, 
  ChevronLeft, 
  ChevronRight,
  PlusCircle,
  HelpCircle,
  LogOut
} from 'lucide-react';

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  isOpen = true, 
  setIsOpen,
  onGenerateReport,
  onOpenCopilot,
  onOpenCitizenRequest,
  onOpenLogin,
  loggedInUser 
}) {
  const menuItems = [
    { id: 'home', label: 'Overview', icon: Home },
    { id: 'alerts', label: 'Dashboard & Risk Feed', icon: ShieldAlert },
    { id: 'map', label: 'Geographic Risk Map', icon: MapPin },
    { id: 'agencies', label: 'Agency Risk Matrix', icon: Building2 },
    { id: 'mps', label: 'MP Allocation Limits', icon: LayoutDashboard },
  ];

  const secondaryItems = [
    { id: 'copilot', label: 'AI Copilot (सक्षम AI)', icon: Sparkles, action: onOpenCopilot, isSpecial: true },
    { id: 'citizen', label: 'Citizen Portal', icon: UserPlus, action: onOpenCitizenRequest },
  ];

  return (
    <aside className={`sidebar-container ${isOpen ? 'expanded' : 'collapsed'}`}>
      {/* Background Animated Floating Glass Bubbles */}
      <div className="sidebar-bubbles-bg">
        <span className="bubble b1" />
        <span className="bubble b2" />
        <span className="bubble b3" />
        <span className="bubble b4" />
      </div>

      {/* User Profile Header with Open/Close Toggle */}
      <div className="sidebar-profile">
        <div className="avatar-circle" onClick={onOpenLogin} style={{ cursor: 'pointer' }} title={loggedInUser?.name || 'MoSPI Admin'}>
          {loggedInUser ? loggedInUser.name.charAt(0).toUpperCase() : 'M'}
        </div>

        {isOpen && (
          <div className="profile-info">
            <div className="profile-name">
              {loggedInUser ? loggedInUser.name : 'MoSPI Admin'}
            </div>
            <div className="profile-role">
              {loggedInUser ? loggedInUser.role : 'Risk Division'}
            </div>
          </div>
        )}

        <button 
          className="sidebar-toggle-btn"
          onClick={() => setIsOpen(!isOpen)}
          title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        >
          {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      {/* Generate Report Primary CTA Button */}
      <div className="sidebar-cta-wrap">
        <button 
          className="sidebar-cta-btn" 
          onClick={onGenerateReport}
          title="Generate Intelligence Report"
        >
          <PlusCircle size={18} className="cta-icon" />
          {isOpen && <span>Generate Intelligence Report</span>}
        </button>
      </div>

      {/* Main Core Platform Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">{isOpen ? 'PLATFORM MODULES' : '•••'}</div>
        
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-item bubble-hover ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
              title={item.label}
            >
              <div className="icon-wrapper">
                <Icon size={18} className="nav-icon" />
                <span className="bubble-effect-glow" />
              </div>
              {isOpen && <span className="nav-label">{item.label}</span>}
            </button>
          );
        })}

        <div className="nav-section-title" style={{ marginTop: '0.75rem' }}>
          {isOpen ? 'INTELLIGENCE & TOOLS' : '•••'}
        </div>

        {secondaryItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-item bubble-hover ${item.isSpecial ? 'special-teal' : ''}`}
              onClick={item.action}
              title={item.label}
            >
              <div className="icon-wrapper">
                <Icon size={18} className="nav-icon" color={item.isSpecial ? '#38bdf8' : undefined} />
                <span className="bubble-effect-glow" />
              </div>
              {isOpen && <span className="nav-label" style={item.isSpecial ? { color: '#38bdf8', fontWeight: 700 } : {}}>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Bottom Footer Actions */}
      <div className="sidebar-footer">
        <button className="sidebar-footer-item bubble-hover" onClick={onOpenCopilot} title="Help Center">
          <HelpCircle size={18} />
          {isOpen && <span>Help Center</span>}
        </button>
        <button className="sidebar-footer-item bubble-hover" onClick={onOpenLogin} title="Logout / Switch Account">
          <LogOut size={18} />
          {isOpen && <span>{loggedInUser ? 'Logout' : 'Admin Login'}</span>}
        </button>
      </div>
    </aside>
  );
}
