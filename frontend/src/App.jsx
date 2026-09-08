import React, { useState, useEffect } from 'react';
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
import DashboardCharts from './components/DashboardCharts';
import { API_BASE_URL } from './apiConfig';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'alerts' | 'map' | 'agencies' | 'mps'
  const [persona, setPersona] = useState('Ministry');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [alertsTotal, setAlertsTotal] = useState(0);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [selectedWorkId, setSelectedWorkId] = useState(null);

  // Modals
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isCitizenRequestOpen, setIsCitizenRequestOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);

  // Risk Intelligence feed filters — pushed to the API (server-side) so the
  // full 48k+ alert dataset is searchable, not just the first page.
  const [alertsSearch, setAlertsSearch] = useState('');
  const [alertsRiskFilter, setAlertsRiskFilter] = useState('ALL');
  const [alertsSignalFilter, setAlertsSignalFilter] = useState('ALL');
  const [alertsPage, setAlertsPage] = useState(0);
  const ALERTS_PAGE_SIZE = 50;

  const fetchDashboardData = () => {
    fetch(`${API_BASE_URL}/api/v1/overview`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Failed to fetch overview stats", err));
  };

  const fetchAlerts = () => {
    setAlertsLoading(true);
    const params = new URLSearchParams({
      limit: String(ALERTS_PAGE_SIZE),
      offset: String(alertsPage * ALERTS_PAGE_SIZE),
    });
    if (alertsRiskFilter !== 'ALL') params.set('risk_level', alertsRiskFilter);
    if (alertsSignalFilter !== 'ALL') params.set('signal_type', alertsSignalFilter);
    if (alertsSearch.trim()) params.set('search', alertsSearch.trim());

    fetch(`${API_BASE_URL}/api/v1/alerts?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setAlerts(data.alerts || []);
        setAlertsTotal(data.total || 0);
        setAlertsLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch alerts", err);
        setAlertsLoading(false);
      });
  };

  useEffect(() => {
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reset to the first page whenever filters or the search term change.
  // (No fetch here — the fetch effect below reacts to the combined change and
  // issues exactly one request per change.)
  useEffect(() => {
    setAlertsPage(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertsRiskFilter, alertsSignalFilter, alertsSearch]);

  // Debounced fetch. Filter/page changes fire immediately; typing an area /
  // MP / work-ID search debounces at 350ms so the full dataset is searchable
  // without a request per keystroke.
  useEffect(() => {
    const t = setTimeout(() => fetchAlerts(), alertsSearch ? 350 : 0);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertsPage, alertsRiskFilter, alertsSignalFilter, alertsSearch]);

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
      {/* Ambient animated gradient background */}
      <div className="bg-aurora" aria-hidden="true">
        <span className="orb orb-1" />
        <span className="orb orb-2" />
        <span className="orb orb-3" />
      </div>

      {/* 1. Main Content Wrapper */}
      <div className="main-wrapper">
        {/* Single Horizontal Glass Navbar */}
        <Header
          persona={persona}
          setPersona={setPersona}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onTriggerAnalytics={handleTriggerAnalytics}
          isRefreshing={isRefreshing}
          onOpenCopilot={openCopilot}
          onOpenCitizenRequest={openCitizenRequest}
          onOpenLogin={openLogin}
          loggedInUser={loggedInUser}
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
            <>
              <DashboardCharts stats={stats} />
              <RiskAlertsFeed
                alerts={alerts}
                total={alertsTotal}
                loading={alertsLoading}
                searchTerm={alertsSearch}
                onSearchChange={setAlertsSearch}
                riskFilter={alertsRiskFilter}
                onRiskFilterChange={setAlertsRiskFilter}
                signalFilter={alertsSignalFilter}
                onSignalFilterChange={setAlertsSignalFilter}
                page={alertsPage}
                onPageChange={setAlertsPage}
                pageSize={ALERTS_PAGE_SIZE}
                onSelectAlert={openInvestigation}
              />
            </>
          )}

          {/* Real Interactive Geographic Risk Map View */}
          {activeTab === 'map' && (
            <GeoRiskMap onSelectAlert={openInvestigation} />
          )}

          {/* Agency Risk Matrix View */}
          {activeTab === 'agencies' && (
            <AgencyRiskMatrix
              onSelectAgency={(ag) => {
                // Open the agency's highest-risk work dossier (agency_id is the
                // IDA name, not a work_id — look up the top-risk work under it)
                setIsCopilotOpen(false);
                setIsCitizenRequestOpen(false);
                setIsLoginOpen(false);
                fetch(`${API_BASE_URL}/api/v1/works?search=${encodeURIComponent(ag.agency_id || ag.agency_name)}&limit=1`)
                  .then(res => res.json())
                  .then(data => {
                    const top = data.works && data.works[0];
                    if (top) openInvestigation(top.work_id);
                  })
                  .catch(err => console.error("Agency work lookup failed", err));
              }}
            />
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
