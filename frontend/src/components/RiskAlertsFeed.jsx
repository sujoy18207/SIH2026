import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  Search, 
  MapPin, 
  User, 
  Building, 
  CheckCircle2, 
  Sparkles, 
  X, 
  MoreVertical
} from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function RiskAlertsFeed({ alerts: initialAlerts = [], onSelectAlert, stats }) {
  const [alerts, setAlerts] = useState(initialAlerts);
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (initialAlerts.length > 0) {
      setAlerts(initialAlerts);
      if (!selectedAlert && initialAlerts.length > 0) {
        setSelectedAlert(initialAlerts[0]);
      }
    } else {
      setLoading(true);
      fetch(`${API_BASE_URL}/api/v1/alerts?limit=50`)
        .then(res => res.json())
        .then(data => {
          const list = data.alerts || [];
          setAlerts(list);
          if (list.length > 0) setSelectedAlert(list[0]);
          setLoading(false);
        })
        .catch(err => {
          console.error("Failed to load alerts", err);
          setLoading(false);
        });
    }
  }, [initialAlerts]);

  const filteredAlerts = alerts.filter(al => {
    if (filterSeverity !== 'ALL' && al.severity !== filterSeverity && al.risk_level !== filterSeverity) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        (al.work_title && al.work_title.toLowerCase().includes(term)) ||
        (al.district && al.district.toLowerCase().includes(term)) ||
        (al.state && al.state.toLowerCase().includes(term)) ||
        (al.work_id && String(al.work_id).toLowerCase().includes(term))
      );
    }
    return true;
  });

  const getScoreCircleClass = (score) => {
    if (score >= 80) return 'risk-circle-critical';
    if (score >= 60) return 'risk-circle-high';
    if (score >= 40) return 'risk-circle-medium';
    return 'risk-circle-low';
  };

  const getStatusPill = (status = 'HALTED') => {
    const s = String(status).toUpperCase();
    if (s.includes('HALT') || s.includes('STOP')) return <span className="status-pill pill-halted">HALTED</span>;
    if (s.includes('DELAY')) return <span className="status-pill pill-delayed">DELAYED</span>;
    return <span className="status-pill pill-delayed">{s}</span>;
  };

  return (
    <div style={{ width: '100%' }}>
      {/* 1. Global Risk Posture Card */}
      <div className="global-risk-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
              Global Risk Posture
            </h2>
            <div style={{ fontSize: '0.775rem', color: '#64748b' }}>
              Total Monitored Works
            </div>
            <div style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.5px' }}>
              {stats?.total_projects ? stats.total_projects.toLocaleString() : '128,081'}
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.775rem', color: '#64748b', marginBottom: '0.2rem' }}>
              System Health
            </div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#10b981', fontWeight: 700, fontSize: '1.15rem' }}>
              <CheckCircle2 size={18} />
              <span>98.4%</span>
            </div>
          </div>
        </div>

        {/* Segmented Risk Progress Bar */}
        <div className="progress-segment-bar">
          <div className="segment-critical" style={{ width: '12%' }} title="Critical: 12%" />
          <div className="segment-high" style={{ width: '28%' }} title="High: 28%" />
          <div className="segment-medium" style={{ width: '45%' }} title="Medium: 45%" />
          <div className="segment-low" style={{ width: '15%' }} title="Low: 15%" />
        </div>

        {/* Legend */}
        <div className="legend-row">
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#ef4444' }} />
            <span>Critical: 1,495 (12%)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#f97316' }} />
            <span>High: 3,488 (28%)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#0284c7' }} />
            <span>Medium: 5,606 (45%)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: '#10b981' }} />
            <span>Low: 1,869 (15%)</span>
          </div>
        </div>
      </div>

      {/* Main Split Layout: Left Feed List + Right Risk Investigation Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedAlert ? '1.4fr 1fr' : '1fr', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: Intelligence Feed */}
        <div>
          {/* Sticky Header Toolbar */}
          <div className="sticky-section-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>
              Intelligence Feed: High-Risk Works
            </h3>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select 
                value={filterSeverity} 
                onChange={(e) => setFilterSeverity(e.target.value)}
                style={{
                  padding: '0.4rem 0.65rem',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e1',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  outline: 'none',
                  background: '#ffffff'
                }}
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical Only</option>
                <option value="HIGH">High Only</option>
                <option value="MEDIUM">Medium Only</option>
              </select>

              <button 
                style={{
                  background: '#ffffff',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  padding: '0.4rem 0.75rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  cursor: 'pointer'
                }}
              >
                <Filter size={14} />
                <span>Filter</span>
              </button>
            </div>
          </div>

          {/* Scrollable Work Alert Cards Container */}
          <div className="sticky-table-wrapper" style={{ maxHeight: '720px', paddingRight: '0.5rem' }}>
            {filteredAlerts.length === 0 ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
                {loading ? 'Scanning eSAKSHI multi-signal records...' : 'No high-risk works matching filters.'}
              </div>
            ) : (
              filteredAlerts.map((al, idx) => {
                const roundedScore = Math.round(Number(al.risk_score) || 85);
                const costCr = al.cost ? (al.cost / 10000000).toFixed(1) : (al.sanctioned_amount ? (al.sanctioned_amount / 10000000).toFixed(1) : '2.5');
                const isSelected = selectedAlert && (selectedAlert.alert_id === al.alert_id || selectedAlert.work_id === al.work_id);

                return (
                  <div 
                    key={al.alert_id || idx}
                    className="work-alert-card"
                    style={{
                      borderColor: isSelected ? '#0d9488' : '#e2e8f0',
                      boxShadow: isSelected ? '0 0 0 2px rgba(13, 148, 136, 0.2)' : 'var(--shadow-sm)',
                      cursor: 'pointer',
                      padding: '1.15rem 1.25rem'
                    }}
                    onClick={() => setSelectedAlert(al)}
                  >
                    {/* Rounded Score Circle Badge */}
                    <div className={`risk-circle-badge ${getScoreCircleClass(roundedScore)}`}>
                      {roundedScore}
                    </div>

                    {/* Middle Info Details */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      {/* Row 1: Title and Status pill in one clean line */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', marginBottom: '0.4rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0, flex: 1 }}>
                          <strong 
                            style={{ 
                              fontSize: '0.95rem', 
                              color: '#0f172a', 
                              fontWeight: 700,
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis'
                            }}
                            title={al.work_title || `Project #${al.work_id}`}
                          >
                            {al.work_title || `Project #${al.work_id}`}
                          </strong>
                        </div>
                        {getStatusPill(al.status || 'HALTED')}
                      </div>

                      {/* Row 2: Metadata row */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', fontSize: '0.8rem', color: '#64748b', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                          <MapPin size={13} color="#94a3b8" />
                          {al.district || 'District'}, {al.state || 'State'}
                        </span>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                          <User size={13} color="#94a3b8" />
                          {al.mp_name || 'Hon\'ble MP'}
                        </span>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                          <Building size={13} color="#94a3b8" />
                          {al.implementing_agency_name || al.agency_name || 'PWD Local'}
                        </span>
                        <span style={{ fontWeight: 700, color: '#0f172a' }}>
                          ₹ {costCr} Cr
                        </span>
                      </div>

                      {/* Row 3: Anomaly Tags */}
                      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                        {al.tags && al.tags.length > 0 ? (
                          al.tags.map((tag, tIdx) => (
                            <span key={tIdx} className="tag-badge">{tag}</span>
                          ))
                        ) : (
                          <>
                            <span className="tag-badge">Expenditure anomaly</span>
                            <span className="tag-badge">Geotag missing &gt; 90d</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Right Action Button */}
                    <div style={{ flexShrink: 0, marginLeft: '0.5rem' }}>
                      <button 
                        className="btn-secondary-outline"
                        style={{ padding: '0.45rem 0.85rem', fontSize: '0.8rem', whiteSpace: 'nowrap' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAlert(al);
                          if (onSelectAlert) onSelectAlert(al.work_id);
                        }}
                      >
                        Inspect Risk
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Risk Investigation Panel */}
        {selectedAlert && (
          <div className="metric-card" style={{ position: 'sticky', top: '80px', maxHeight: 'calc(100vh - 120px)', overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.85rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} color="#0d9488" />
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>
                  Risk Investigation
                </h3>
              </div>
              <button 
                onClick={() => setSelectedAlert(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>Active Context</div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0f172a', margin: '0.2rem 0' }}>
                {selectedAlert.work_title || `Project #${selectedAlert.work_id}`}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#ef4444', fontWeight: 700, fontSize: '0.85rem' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }} />
                <span>Risk Score: {Math.round(selectedAlert.risk_score || 94)} ({selectedAlert.risk_level || selectedAlert.severity || 'Critical'})</span>
              </div>
            </div>

            {/* AI Synthesis Box */}
            <div style={{ background: '#f0fdfa', border: '1px solid #ccfbf1', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#0f766e', fontWeight: 700, fontSize: '0.8rem', marginBottom: '0.4rem' }}>
                <Sparkles size={15} />
                <span>AI Synthesis</span>
              </div>
              <p style={{ fontSize: '0.825rem', color: '#134e4a', lineHeight: 1.5 }}>
                {selectedAlert.narrative_explanation || selectedAlert.explanation || 
                  `Pattern matching indicates a high probability of fund diversion. The expenditure rate accelerated significantly, conflicting with the lack of updated geotagged physical progress.`}
              </p>
            </div>

            {/* Risk Factors Breakdown */}
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>
                Risk Factors
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ borderLeft: '3px solid #ef4444', paddingLeft: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                    <strong style={{ fontSize: '0.825rem', color: '#0f172a' }}>Financial Anomaly</strong>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ef4444' }}>wt: 0.65</span>
                  </div>
                  <p style={{ fontSize: '0.775rem', color: '#64748b' }}>
                    Sudden drawdown of remaining funds despite incomplete physical milestones in MPR.
                  </p>
                </div>

                <div style={{ borderLeft: '3px solid #f97316', paddingLeft: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                    <strong style={{ fontSize: '0.825rem', color: '#0f172a' }}>Geospatial Void</strong>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f97316' }}>wt: 0.25</span>
                  </div>
                  <p style={{ fontSize: '0.775rem', color: '#64748b' }}>
                    Mandatory monthly Bhuvan app image upload missed for consecutive cycles.
                  </p>
                </div>
              </div>
            </div>

            {/* Bottom Action */}
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid #e2e8f0' }}>
              <button 
                className="btn-primary-dark"
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => {
                  if (onSelectAlert) onSelectAlert(selectedAlert.work_id);
                }}
              >
                Escalate File
              </button>
              
              <button 
                className="icon-btn"
                style={{ border: '1px solid #e2e8f0', width: '38px', height: '38px', borderRadius: '8px' }}
                title="More Actions"
              >
                <MoreVertical size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
