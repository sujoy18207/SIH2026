import React, { useState, useEffect } from 'react';
import { ShieldAlert, Search, AlertOctagon, ArrowUpRight, Filter, ChevronLeft, ChevronRight, Layers, FileText } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function RiskAlertsFeed({ alerts: initialAlerts = [], onSelectAlert }) {
  const [viewMode, setViewMode] = useState('alerts'); // 'alerts' | 'all_works'
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [signalFilter, setSignalFilter] = useState('ALL');
  const [stateFilter, setStateFilter] = useState('ALL');
  
  // Data state
  const [items, setItems] = useState(initialAlerts);
  const [totalCount, setTotalCount] = useState(initialAlerts.length);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  // Sync initial alerts
  useEffect(() => {
    if (initialAlerts.length > 0 && viewMode === 'alerts' && !searchTerm && riskFilter === 'ALL' && signalFilter === 'ALL' && stateFilter === 'ALL') {
      setItems(initialAlerts);
      setTotalCount(initialAlerts.length);
    }
  }, [initialAlerts]);

  // Fetch from backend based on viewMode, search, and filters
  useEffect(() => {
    setLoading(true);
    const offset = (page - 1) * pageSize;
    
    let endpoint = '';
    const params = new URLSearchParams();
    params.set('limit', String(pageSize));
    params.set('offset', String(offset));

    if (searchTerm.trim()) params.set('search', searchTerm.trim());
    if (stateFilter !== 'ALL') params.set('state', stateFilter);
    if (riskFilter !== 'ALL') params.set('risk_level', riskFilter);

    if (viewMode === 'alerts') {
      if (signalFilter !== 'ALL') params.set('signal_type', signalFilter);
      endpoint = `${API_BASE_URL}/api/v1/alerts?${params.toString()}`;
    } else {
      endpoint = `${API_BASE_URL}/api/v1/works?${params.toString()}`;
    }

    const timer = setTimeout(() => {
      fetch(endpoint)
        .then(res => res.json())
        .then(data => {
          if (viewMode === 'alerts') {
            setItems(data.alerts || []);
            setTotalCount(data.total || (data.alerts ? data.alerts.length : 0));
          } else {
            setItems(data.works || []);
            setTotalCount(data.total || (data.works ? data.works.length : 0));
          }
          setLoading(false);
        })
        .catch(err => {
          console.error("Failed to fetch works data", err);
          setLoading(false);
        });
    }, 200); // 200ms debounce

    return () => clearTimeout(timer);
  }, [viewMode, searchTerm, riskFilter, signalFilter, stateFilter, page, pageSize]);

  // Reset page to 1 when filters change
  const handleSearchChange = (val) => {
    setSearchTerm(val);
    setPage(1);
  };

  const handleStateChange = (val) => {
    setStateFilter(val);
    setPage(1);
  };

  const handleRiskChange = (val) => {
    setRiskFilter(val);
    setPage(1);
  };

  const getRiskBadge = (level = 'Medium', score = 0) => {
    const safeScore = typeof score === 'number' ? score : (Number(score) || 0);
    const safeLevel = level ? String(level) : 'Medium';
    const lvlClass = safeLevel.toLowerCase();
    return (
      <span className={`badge-risk ${lvlClass}`}>
        <AlertOctagon size={12} />
        {safeScore.toFixed(0)} • {safeLevel}
      </span>
    );
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  const popularStates = [
    "West Bengal", "Maharashtra", "Uttar Pradesh", "Tamil Nadu", 
    "Karnataka", "Gujarat", "Bihar", "Punjab", "Rajasthan", "Kerala"
  ];

  return (
    <div className="goi-card">
      
      {/* Card Header with View Toggle & Search */}
      <div className="goi-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <div>
            <div className="goi-card-title">
              <ShieldAlert size={20} color={viewMode === 'alerts' ? '#dc2626' : '#0284c7'} />
              {viewMode === 'alerts' ? 'Risk Intelligence & Anomaly Priority Feed' : 'All Monitored Works Directory'}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.2rem' }}>
              Showing {totalCount.toLocaleString()} {viewMode === 'alerts' ? 'flagged priority works' : 'total monitored works'} across India
            </div>
          </div>

          {/* Dataset View Mode Switcher */}
          <div style={{ display: 'flex', background: '#f1f5f9', padding: '0.2rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
            <button
              onClick={() => { setViewMode('alerts'); setPage(1); }}
              style={{
                padding: '0.35rem 0.85rem',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: viewMode === 'alerts' ? '#ffffff' : 'transparent',
                color: viewMode === 'alerts' ? '#dc2626' : '#64748b',
                boxShadow: viewMode === 'alerts' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
              }}
            >
              Priority Alerts (1,673)
            </button>
            <button
              onClick={() => { setViewMode('all_works'); setPage(1); }}
              style={{
                padding: '0.35rem 0.85rem',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: viewMode === 'all_works' ? '#ffffff' : 'transparent',
                color: viewMode === 'all_works' ? '#0284c7' : '#64748b',
                boxShadow: viewMode === 'all_works' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
              }}
            >
              All Monitored Works (10,000+)
            </button>
          </div>
        </div>

        {/* Search & Filters Toolbar */}
        <div style={{ display: 'flex', gap: '0.55rem', flexWrap: 'wrap', alignItems: 'center' }}>
          
          {/* Live Search Input */}
          <div style={{ position: 'relative', width: '270px' }}>
            <Search size={14} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
            <input
              type="text"
              placeholder="Search MP / State / Work ID / Word..."
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="goi-input"
              style={{ paddingLeft: '2.2rem' }}
            />
            {searchTerm && (
              <button
                onClick={() => handleSearchChange('')}
                style={{ position: 'absolute', right: '10px', top: '8px', border: 'none', background: 'transparent', color: '#94a3b8', cursor: 'pointer', fontSize: '0.85rem' }}
              >
                ✕
              </button>
            )}
          </div>

          {/* State / UT Filter */}
          <select
            value={stateFilter}
            onChange={(e) => handleStateChange(e.target.value)}
            className="goi-select"
          >
            <option value="ALL">All States / UTs</option>
            {popularStates.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => handleRiskChange(e.target.value)}
            className="goi-select"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="Critical">Critical (80–100)</option>
            <option value="High">High (60–79)</option>
            <option value="Medium">Medium (30–59)</option>
            <option value="Low">Low (0–29)</option>
          </select>

          {/* Signal Filter (only in alerts mode) */}
          {viewMode === 'alerts' && (
            <select
              value={signalFilter}
              onChange={(e) => { setSignalFilter(e.target.value); setPage(1); }}
              className="goi-select"
            >
              <option value="ALL">All Anomaly Types</option>
              <option value="COST_ANOMALY">Cost Overrun Anomaly</option>
              <option value="DUPLICATE_WORK">Duplicate Work Match</option>
              <option value="ISOLATION_FOREST">Unsupervised ML Outlier</option>
              <option value="RULE_VIOLATION">Compliance Rule Violation</option>
              <option value="AGENCY_RISK">High-Risk Executing Agency</option>
            </select>
          )}

        </div>
      </div>

      {/* Table Feed */}
      <div className="goi-table-container">
        <table className="goi-table">
          <thead>
            <tr>
              <th style={{ width: '130px' }}>Risk Score</th>
              <th>Work Details & Location</th>
              <th>Member of Parliament (MP)</th>
              <th>{viewMode === 'alerts' ? 'Primary Evidence Signal' : 'Category / Financials'}</th>
              <th style={{ width: '110px', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '3.5rem 1rem', color: '#0d9488', fontWeight: 600 }}>
                  Searching and retrieving records from database...
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '3.5rem 1rem', color: '#64748b' }}>
                  <p style={{ fontWeight: 600, fontSize: '0.95rem', color: '#0f2744' }}>No matching records found for "{searchTerm}"</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.35rem' }}>Try clearing the search box or selecting "All States" / "All Risk Levels".</p>
                  <button
                    onClick={() => { setSearchTerm(''); setRiskFilter('ALL'); setStateFilter('ALL'); setSignalFilter('ALL'); }}
                    className="btn-esakshi-outline"
                    style={{ marginTop: '1rem', fontSize: '0.8rem' }}
                  >
                    Reset All Filters
                  </button>
                </td>
              </tr>
            ) : (
              items.map((item) => {
                const workId = item.work_id || item.project_id;
                const riskScore = item.risk_score ?? item.composite_risk_score ?? 0;
                const riskLvl = item.risk_level || (riskScore >= 40 ? 'Critical' : riskScore >= 30 ? 'High' : riskScore >= 15 ? 'Medium' : 'Low');
                const signals = Array.isArray(item.triggering_signals) ? item.triggering_signals : [];
                const primarySignal = signals[0];

                return (
                  <tr
                    key={item.alert_id || workId || Math.random()}
                    onClick={() => onSelectAlert && onSelectAlert(workId)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      {getRiskBadge(riskLvl, riskScore)}
                    </td>

                    <td>
                      <div style={{ fontWeight: 700, color: '#0f2744', fontSize: '0.875rem' }}>
                        {item.work_title || item.work_description || `Project #${workId}`}
                      </div>
                      <div style={{ fontSize: '0.775rem', color: '#64748b', marginTop: '0.15rem' }}>
                        {item.district ? `${item.district}, ` : ''}{item.state || 'India'} {item.constituency ? `(${item.constituency})` : ''} • ID: {workId}
                      </div>
                    </td>

                    <td>
                      <div style={{ fontWeight: 600, color: '#334155', fontSize: '0.85rem' }}>
                        {item.mp_name || 'Hon\'ble MP'}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        {item.implementing_agency_name ? String(item.implementing_agency_name).slice(0, 30) : 'District Agency'}
                      </div>
                    </td>

                    <td>
                      {viewMode === 'alerts' ? (
                        primarySignal ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <span style={{
                              display: 'inline-block',
                              width: '7px',
                              height: '7px',
                              borderRadius: '50%',
                              background: riskLvl === 'Critical' ? '#dc2626' : '#ea580c'
                            }} />
                            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569' }}>
                              {primarySignal.evidence_text ? String(primarySignal.evidence_text).slice(0, 50) : (primarySignal.title || primarySignal.signal_type)}
                            </span>
                          </div>
                        ) : (
                          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Statistical Outlier</span>
                        )
                      ) : (
                        <div>
                          <div style={{ fontSize: '0.78rem', color: '#0f2744', fontWeight: 600 }}>{item.work_category || 'Normal/Others'}</div>
                          <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.1rem' }}>
                            Status: <strong style={{ color: item.work_status === 'Completed' ? '#16a34a' : '#0284c7' }}>{item.work_status || 'In Progress'}</strong> • ₹{(Number(item.expenditure || item.sanctioned_amount || 0)/100000).toFixed(1)}L
                          </div>
                        </div>
                      )}
                    </td>

                    <td style={{ textAlign: 'right' }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectAlert) onSelectAlert(workId);
                        }}
                        className="btn-esakshi-outline"
                        style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                      >
                        Inspect
                        <ArrowUpRight size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div style={{
        padding: '0.9rem 1.5rem',
        borderTop: '1px solid var(--goi-border)',
        background: '#ffffff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
          Showing {items.length > 0 ? ((page - 1) * pageSize + 1).toLocaleString() : 0} to {Math.min(page * pageSize, totalCount).toLocaleString()} of <strong>{totalCount.toLocaleString()}</strong> projects
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', color: '#64748b' }}>
            <span>Per page:</span>
            <select
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
              className="goi-select"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.78rem' }}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="btn-esakshi-outline"
              style={{ padding: '0.3rem 0.6rem', opacity: page <= 1 ? 0.5 : 1, cursor: page <= 1 ? 'not-allowed' : 'pointer' }}
            >
              <ChevronLeft size={14} />
              Prev
            </button>

            <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0 0.5rem', color: '#0f2744' }}>
              Page {page} of {totalPages}
            </span>

            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="btn-esakshi-outline"
              style={{ padding: '0.3rem 0.6rem', opacity: page >= totalPages ? 0.5 : 1, cursor: page >= totalPages ? 'not-allowed' : 'pointer' }}
            >
              Next
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
