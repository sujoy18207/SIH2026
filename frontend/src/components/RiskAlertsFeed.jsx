import React from 'react';
import {
  ShieldAlert, Search, ArrowUpRight, CheckCircle, AlertOctagon, ChevronLeft, ChevronRight, Loader2
} from 'lucide-react';

const SIGNAL_OPTIONS = [
  { value: 'ALL', label: 'All Signal Categories' },
  { value: 'VENDOR', label: 'Multi-Vendor Splitting' },
  { value: 'OVERRUN', label: 'Completion / Disbursal Overrun' },
  { value: 'DUPLICATE', label: 'NLP Duplicate Candidate' },
  { value: 'ZOMBIE', label: 'Stalled / Zombie Work' },
  { value: 'TIMELINE', label: 'Impossible Timeline' },
  { value: 'NO_PAYMENTS', label: 'Completed Without Payments' },
  { value: 'MISSING', label: 'Missing File Evidence' },
  { value: 'UNVERIFIED', label: 'Unverified Completion' },
  { value: 'STATISTICAL', label: 'ML Outlier' },
];

export default function RiskAlertsFeed({
  alerts,
  total,
  loading,
  searchTerm,
  onSearchChange,
  riskFilter,
  onRiskFilterChange,
  signalFilter,
  onSignalFilterChange,
  page,
  onPageChange,
  pageSize,
  onSelectAlert,
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : page * pageSize + 1;
  const to = Math.min(total, (page + 1) * pageSize);

  const getRiskBadge = (level, score) => {
    const lvlClass = (level || 'low').toLowerCase();
    return (
      <span className={`badge-risk ${lvlClass}`}>
        <AlertOctagon size={12} />
        {Number(score || 0).toFixed(0)} • {level}
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
            ({total.toLocaleString('en-IN')} Works Flagged for Verification)
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={14} color="#6b7280" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search MP / MLA / Constituency / District / Work ID..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
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
            onChange={(e) => onRiskFilterChange(e.target.value)}
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
            <option value="Low">Low (0-25)</option>
          </select>

          <select
            value={signalFilter}
            onChange={(e) => onSignalFilterChange(e.target.value)}
            style={{
              padding: '0.4rem 0.75rem',
              background: '#ffffff',
              border: '1px solid var(--goi-border)',
              borderRadius: '4px',
              color: '#1a252c',
              fontSize: '0.825rem'
            }}
          >
            {SIGNAL_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
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
            {loading && alerts.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Loader2 size={18} className="spin" /> Loading risk alerts across the full eSAKSHI dataset…
                  </span>
                </td>
              </tr>
            ) : alerts.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                  No alerts match the current filters. Try clearing the search term or widening the risk level.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.alert_id} onClick={() => onSelectAlert(alert.work_id)}>
                  <td style={{ fontWeight: 700, color: '#173a67' }}>{alert.work_id}</td>
                  <td>{getRiskBadge(alert.risk_level, alert.risk_score)}</td>
                  <td style={{ fontWeight: 600, color: '#1e40af' }}>
                    {alert.evidence_confidence_score != null ? Number(alert.evidence_confidence_score).toFixed(0) : '—'}%
                  </td>
                  <td style={{ fontWeight: 600, color: (alert.data_quality_score || 0) < 70 ? '#d97706' : '#15803d' }}>
                    {alert.data_quality_score != null ? Number(alert.data_quality_score).toFixed(0) : '—'}%
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
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination footer — full dataset is reachable, 50 per page */}
      {!loading && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          padding: '0.85rem 0.25rem 0.1rem',
          borderTop: '1px solid var(--goi-border)',
          marginTop: '0.75rem'
        }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--goi-text-muted)' }}>
            Showing <strong>{from.toLocaleString('en-IN')}–{to.toLocaleString('en-IN')}</strong> of{' '}
            <strong>{total.toLocaleString('en-IN')}</strong> flagged works
          </span>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <button
              className="btn-esakshi-outline"
              disabled={page === 0}
              onClick={() => onPageChange(page - 1)}
              style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
            >
              <ChevronLeft size={14} /> Prev
            </button>
            <span style={{ fontSize: '0.78rem', color: 'var(--goi-text-muted)' }}>
              Page <strong>{page + 1}</strong> / {totalPages.toLocaleString('en-IN')}
            </span>
            <button
              className="btn-esakshi-outline"
              disabled={page + 1 >= totalPages}
              onClick={() => onPageChange(page + 1)}
              style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
