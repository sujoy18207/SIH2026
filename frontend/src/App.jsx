import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroLanding from './components/HeroLanding';
import OverviewCards from './components/OverviewCards';
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
  const [persona, setPersona] = useState('Ministry');
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'alerts' | 'map' | 'agencies' | 'mps'
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedWorkId, setSelectedWorkId] = useState(null);
  
  // Modals
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isCitizenRequestOpen, setIsCitizenRequestOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboardData = () => {
    setIsRefreshing(true);
    fetch(`${API_BASE_URL}/api/v1/overview`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Failed to fetch overview stats", err));

    fetch(`${API_BASE_URL}/api/v1/alerts?limit=100`)
      .then(res => res.json())
      .then(data => {
        setAlerts(data.alerts || []);
        setIsRefreshing(false);
      })
      .catch(err => {
        console.error("Failed to fetch alerts", err);
        setIsRefreshing(false);
      });
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleTriggerAnalytics = () => {
    setIsRefreshing(true);
    fetch(`${API_BASE_URL}/api/v1/analytics/run`, { method: 'POST' })
      .then(res => res.json())
      .then(() => fetchDashboardData())
      .catch(err => {
        console.error("Analytics failed", err);
        setIsRefreshing(false);
      });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f4f6f9' }}>
      <Header
        persona={persona}
        setPersona={setPersona}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onTriggerAnalytics={handleTriggerAnalytics}
        isRefreshing={isRefreshing}
        onOpenCopilot={() => setIsCopilotOpen(true)}
        onOpenCitizenRequest={() => setIsCitizenRequestOpen(true)}
        onOpenLogin={() => setIsLoginOpen(true)}
        loggedInUser={loggedInUser}
      />

      {/* Landing Hero View */}
      {activeTab === 'home' && (
        <HeroLanding
          onNavigateTab={(tab) => setActiveTab(tab)}
          onOpenCitizenRequest={() => setIsCitizenRequestOpen(true)}
          onOpenLogin={() => setIsLoginOpen(true)}
          onOpenCopilot={() => setIsCopilotOpen(true)}
        />
      )}

      {/* Dashboard & Analytics View */}
      {activeTab !== 'home' && (
        <main style={{ maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '2rem 1.5rem', flex: 1 }}>
          {/* KPI Overview Summary Cards */}
          <OverviewCards stats={stats} />

          {/* Tab Content */}
          {activeTab === 'alerts' && (
            <RiskAlertsFeed alerts={alerts} onSelectAlert={(wid) => setSelectedWorkId(wid)} />
          )}

          {activeTab === 'map' && (
            <GeoRiskMap onSelectAlert={(wid) => setSelectedWorkId(wid)} />
          )}

          {activeTab === 'agencies' && (
            <AgencyRiskMatrix />
          )}

          {activeTab === 'mps' && (
            <MPAllocatedLimitsTable />
          )}
        </main>
      )}

      {/* Investigation Drawer Dossier */}
      <InvestigationDrawer
        workId={selectedWorkId}
        onClose={() => setSelectedWorkId(null)}
        onSubmitReview={() => fetchDashboardData()}
      />

      {/* AI Copilot Modal */}
      <AICopilotModal
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
      />

      {/* Citizen Request Portal Modal */}
      <CitizenRequestModal
        isOpen={isCitizenRequestOpen}
        onClose={() => setIsCitizenRequestOpen(false)}
      />

      {/* Official eSAKSHI Split-Screen Login Modal */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLoginSuccess={(user) => {
          setLoggedInUser(user);
          setActiveTab('alerts');
        }}
      />

      {/* Official Government Footer */}
      <Footer />
    </div>
  );
}
