import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import OverviewCards from './components/OverviewCards';
import RiskAlertsFeed from './components/RiskAlertsFeed';
import AgencyRiskMatrix from './components/AgencyRiskMatrix';
import InvestigationDrawer from './components/InvestigationDrawer';
import AICopilotModal from './components/AICopilotModal';
import Footer from './components/Footer';

export default function App() {
  const [persona, setPersona] = useState('Ministry');
  const [activeTab, setActiveTab] = useState('alerts'); // 'alerts' | 'agencies'
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedWorkId, setSelectedWorkId] = useState(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboardData = () => {
    setIsRefreshing(true);
    fetch('http://localhost:8000/api/v1/overview')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error("Failed to fetch overview stats", err));

    fetch('http://localhost:8000/api/v1/alerts?limit=100')
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
    fetch('http://localhost:8000/api/v1/analytics/run', { method: 'POST' })
      .then(res => res.json())
      .then(() => fetchDashboardData())
      .catch(err => {
        console.error("Analytics failed", err);
        setIsRefreshing(false);
      });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        persona={persona}
        setPersona={setPersona}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onTriggerAnalytics={handleTriggerAnalytics}
        isRefreshing={isRefreshing}
        onOpenCopilot={() => setIsCopilotOpen(true)}
      />

      <main style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', padding: '1.5rem 1.5rem', flex: 1 }}>
        {/* KPI Overview Summary Cards */}
        <OverviewCards stats={stats} />

        {/* Tab Content */}
        {activeTab === 'alerts' && (
          <RiskAlertsFeed alerts={alerts} onSelectAlert={(wid) => setSelectedWorkId(wid)} />
        )}

        {activeTab === 'agencies' && (
          <AgencyRiskMatrix />
        )}
      </main>

      {/* Investigation Drawer */}
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

      {/* Official Government Footer */}
      <Footer />
    </div>
  );
}
