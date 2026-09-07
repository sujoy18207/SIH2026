import React, { useState } from 'react';
import { ShieldAlert, Search, Filter, ArrowUpRight, CheckCircle, AlertOctagon, ShieldCheck, FileSpreadsheet } from 'lucide-react';

export default function RiskAlertsFeed({ alerts, onSelectAlert }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [signalFilter, setSignalFilter] = useState('ALL');

  const filteredAlerts = alerts.filter(alert => {
    if (riskFilter !== 'ALL' && alert.risk_level !== riskFilter) return false;
    if (signalFilter !== 'ALL') {
      const hasSignal = alert.triggering_signals.some(s => s.signal_type.includes(signalFilter));
      if (!hasSignal) return false;
    }
    if (searchTerm) {
      const s = searchTerm.toLowerCase().trim();
      const match = (
        (alert.work_id && alert.work_id.toLowerCase().includes(s)) ||
        (alert.work_title && alert.work_title.toLowerCase().includes(s)) ||
        (alert.district && alert.district.toLowerCase().includes(s)) ||
        (alert.state && alert.state.toLowerCase().includes(s)) ||
        (alert.constituency && alert.constituency.toLowerCase().includes(s)) ||
        (alert.mp_name && alert.mp_name.toLowerCase().includes(s)) ||
        (alert.implementing_agency_name && alert.implementing_agency_name.toLowerCase().includes(s)) ||
        // Support searching "MLA" / "MP" / "Representative" / local terms
        (s.includes('mla') || s.includes('mp') || s.includes('rep'))
      );
      if (!match) return false;
    }
    return true;
  });

  const getRiskBadge = (level, score) => {
    const lvlClass = level.toLowerCase();
    return (
      <span className={`badge-risk ${lvlClass}`}>
        <AlertOctagon size={12} />
        {score.toFixed(0)} • {level}
      </span>
    );
  };

  return (
    <div className="goi-card">
      <div className="goi-card-header">
        <div className="goi-card-title">
          <ShieldAlert size={20} color="#c53030" />
          Risk Intelligence & Priority Review Feed
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--goi-text-muted)', marginLeft: '0.5rem' }}>
            ({filteredAlerts.length} Works Flagged for Verification)
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={14} color="#6b7280" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search MP / MLA / Constituency / District / Work ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.4rem 0.5rem 0.4rem 2.2rem',
                background: '#ffffff',
                border: '1px solid var(--goi-border)',
                borderRadius: '4px',
                color: '#1a252c',
                fontSize: '0.825rem'
              }}
            />
          </div>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            style={{
              padding: '0.4rem 0.75rem',
              background: '#ffffff',
              border: '1px solid var(--goi-border)',
              borderRadius: '4px',
              color: '#1a252c',
              fontSize: '0.825rem'
            }}
          >
            <option value="ALL">All Risk Levels</option>
            <option value="Critical">Critical (76-100)</option>
            <option value="High">High (51-75)</option>
            <option value="Medium">Medium (26-50)</option>
          </select>

          <select
            value={signalFilter}
            onChange={(e) => setSignalFilter(e.target.value)}
            style={{
              padding: '0.4rem 0.75rem',
              background: '#ffffff',
              border: '1px solid var(--goi-border)',
              borderRadius: '4px',
              color: '#1a252c',
              fontSize: '0.825rem'
            }}
          >
            <option value="ALL">All Signal Categories</option>
            <option value="VENDOR">Multi-Vendor Splitting</option>
            <option value="OVERRUN">Completion Cost Overrun</option>
            <option value="DUPLICATE">NLP Duplicate Candidate</option>
            <option value="ZOMBIE">Stalled / Zombie Work</option>
            <option value="TIMELINE">Impossible Timeline</option>
            <option value="NO_PAYMENTS">Completed Without Payments</option>
            <option value="MISSING">Missing File Evidence</option>
            <option value="STATISTICAL">ML Outlier</option>
          </select>
        </div>
      </div>

      <div className="custom-table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Work ID</th>
              <th>Risk Score</th>
              <th>Evidence Confidence</th>
              <th>Data Quality</th>
              <th>Work Description</th>
              <th>State / District</th>
              <th>Executing Agency</th>
              <th>Audit Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredAlerts.slice(0, 50).map((alert) => (
              <tr key={alert.alert_id} onClick={() => onSelectAlert(alert.work_id)}>
                <td style={{ fontWeight: 700, color: '#173a67' }}>{alert.work_id}</td>
                <td>{getRiskBadge(alert.risk_level, alert.risk_score)}</td>
                <td style={{ fontWeight: 600, color: '#1e40af' }}>
                  {alert.evidence_confidence_score?.toFixed(0)}%
                </td>
                <td style={{ fontWeight: 600, color: alert.data_quality_score < 70 ? '#d97706' : '#15803d' }}>
                  {alert.data_quality_score?.toFixed(0)}%
                </td>
                <td style={{ maxWidth: '240px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {alert.work_title}
                </td>
                <td>{alert.state} / {alert.district}</td>
                <td>{alert.implementing_agency_name}</td>
                <td>
                  {alert.is_reviewed ? (
                    <span style={{ color: '#15803d', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.2rem', fontWeight: 700 }}>
                      <CheckCircle size={14} /> Verified
                    </span>
                  ) : (
                    <span style={{ color: '#6b7280', fontSize: '0.78rem' }}>Pending Review</span>
                  )}
                </td>
                <td>
                  <button
                    className="btn-goi-primary"
                    style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectAlert(alert.work_id);
                    }}
                  >
                    Investigate <ArrowUpRight size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
