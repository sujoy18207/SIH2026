import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import HeroLanding from './components/HeroLanding';
import RiskAlertsFeed from './components/RiskAlertsFeed';
import GeoRiskMap from './components/GeoRiskMap';
import AgencyRiskMatrix from './components/AgencyRiskMatrix';
import MPAllocatedLimitsTable from './components/MPAllocatedLimitsTable';
import InvestigationDrawer from './components/InvestigationDrawer';
import AICopilotModal from './components/AICopilotModal';
import CitizenRequestModal from './components/CitizenRequestModal';
import LoginModal from './components/LoginModal';
import Footer from './components/Footer';
import { API_BASE_URL } from './apiConfig';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'alerts' | 'map' | 'agencies' | 'mps'
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedWorkId, setSelectedWorkId] = useState(null);
  
  // Modals
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isCitizenRequestOpen, setIsCitizenRequestOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);

  const fetchDashboardData = () => {
    fetch(`${API_BASE_URL}/api/v1/overview`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Failed to fetch overview stats", err));

    fetch(`${API_BASE_URL}/api/v1/alerts?limit=100`)
      .then(res => res.json())
      .then(data => {
        setAlerts(data.alerts || []);
      })
      .catch(err => console.error("Failed to fetch alerts", err));
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleGenerateReport = () => {
    window.open(`${API_BASE_URL}/api/v1/overview`, '_blank');
  };

  // Safe modal triggers (opens only one at a time)
  const openCopilot = () => {
    setSelectedWorkId(null);
    setIsCitizenRequestOpen(false);
    setIsLoginOpen(false);
    setIsCopilotOpen(true);
  };

  const openCitizenRequest = () => {
    setSelectedWorkId(null);
    setIsCopilotOpen(false);
    setIsLoginOpen(false);
    setIsCitizenRequestOpen(true);
  };

  const openLogin = () => {
    setSelectedWorkId(null);
    setIsCopilotOpen(false);
    setIsCitizenRequestOpen(false);
    setIsLoginOpen(true);
  };

  const openInvestigation = (wid) => {
    setIsCopilotOpen(false);
    setIsCitizenRequestOpen(false);
    setIsLoginOpen(false);
    setSelectedWorkId(wid);
  };

  return (
    <div className="app-container">
      {/* 1. Dark Navy Collapsible Left Sidebar with Bubble Effect */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        onGenerateReport={handleGenerateReport}
        onOpenCopilot={openCopilot}
        onOpenCitizenRequest={openCitizenRequest}
        onOpenLogin={openLogin}
        loggedInUser={loggedInUser}
      />

      {/* 2. Main Content Wrapper */}
      <div className="main-wrapper">
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onOpenCopilot={openCopilot}
          onOpenLogin={openLogin}
          loggedInUser={loggedInUser}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
        />

        {/* Page Content View */}
        <main className="page-content">
          {/* Overview / Landing View */}
          {activeTab === 'home' && (
            <HeroLanding
              onNavigateTab={(tab) => setActiveTab(tab)}
              onOpenCitizenRequest={openCitizenRequest}
              onOpenCopilot={openCopilot}
              stats={stats}
            />
          )}

          {/* Risk Dashboard & Intelligence Feed View */}
          {activeTab === 'alerts' && (
            <RiskAlertsFeed
              alerts={alerts}
              onSelectAlert={openInvestigation}
              stats={stats}
            />
          )}

          {/* Real Interactive Geographic Risk Map View */}
          {activeTab === 'map' && (
            <GeoRiskMap onSelectAlert={openInvestigation} />
          )}

          {/* Agency Risk Matrix View */}
          {activeTab === 'agencies' && (
            <AgencyRiskMatrix onSelectAgency={(ag) => openInvestigation(ag.agency_id)} />
          )}

          {/* MP Allocation View */}
          {activeTab === 'mps' && (
            <MPAllocatedLimitsTable />
          )}
        </main>

        {/* Sticky Bottom Government Footer */}
        <Footer />
      </div>

      {/* Deep-Dive Investigation Dossier Drawer (Fixed Overlay) */}
      <InvestigationDrawer
        workId={selectedWorkId}
        onClose={() => setSelectedWorkId(null)}
        onSubmitReview={() => fetchDashboardData()}
      />

      {/* AI Copilot Modal (Fixed Overlay) */}
      <AICopilotModal
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
      />

      {/* Citizen Request Portal Modal (Fixed Overlay) */}
      <CitizenRequestModal
        isOpen={isCitizenRequestOpen}
        onClose={() => setIsCitizenRequestOpen(false)}
      />

      {/* Official Officer Login Modal (Fixed Overlay) */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(user) => {
          setLoggedInUser(user);
          setActiveTab('alerts');
        }}
      />
    </div>
  );
}
