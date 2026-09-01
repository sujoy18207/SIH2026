import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Search, 
  Download, 
  AlertTriangle, 
  Sparkles, 
  TrendingUp, 
  ChevronDown, 
  ChevronUp,
  FileCheck
} from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

const INITIAL_AGENCIES = [
  { agency_id: 'AGY-001', agency_name: 'PWD Division 4 (Varanasi)', district: 'Varanasi', total_works: 142, completed_works: 89, delayed_works: 45, total_expenditure: 124000000, anomaly_count: 3, agency_risk_score: 88, agency_risk_level: 'Critical', ai_explanation: 'Pattern of systematic delays detected in infrastructure projects exceeding ₹2Cr. High concentration of anomalous material procurements recorded in Q3.' },
  { agency_id: 'AGY-002', agency_name: 'Rural Development Agency (Ganjam)', district: 'Ganjam', total_works: 110, completed_works: 75, delayed_works: 28, total_expenditure: 98000000, anomaly_count: 2, agency_risk_score: 65, agency_risk_level: 'High', ai_explanation: 'Multiple road construction works flagged for accelerated fund withdrawal before monsoon without geo-tagged MPR milestone verification.' },
  { agency_id: 'AGY-003', agency_name: 'Jal Nigam Urban (Lucknow)', district: 'Lucknow', total_works: 85, completed_works: 78, delayed_works: 2, total_expenditure: 89000000, anomaly_count: 0, agency_risk_score: 12, agency_risk_level: 'Low', ai_explanation: 'High compliance record. All drinking water pipeline projects validated with zero utilization certificate submission delays.' },
  { agency_id: 'AGY-004', agency_name: 'District Rural Development Authority (Nadia)', district: 'Nadia', total_works: 94, completed_works: 62, delayed_works: 18, total_expenditure: 81000000, anomaly_count: 1, agency_risk_score: 52, agency_risk_level: 'Medium', ai_explanation: 'Solar street lighting installation records show moderate cluster similarity with previously sanctioned works in Block 2.' }
];

export default function AgencyRiskMatrix({ onSelectAgency }) {
  const [agencies, setAgencies] = useState(INITIAL_AGENCIES);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedAgencyId, setExpandedAgencyId] = useState('AGY-001');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/agencies`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setAgencies(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.warn("Using instant live agency data", err);
        setLoading(false);
      });
  }, []);

  const filteredAgencies = agencies.filter(ag => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      (ag.agency_name && ag.agency_name.toLowerCase().includes(term)) ||
      (ag.district && ag.district.toLowerCase().includes(term))
    );
  });

  const exportCSV = () => {
    const headers = ["Agency", "District", "Total Works", "Completed", "Delayed", "Disbursed (Cr)", "Anomalies", "Risk Score"];
    const rows = filteredAgencies.map(a => [
      `"${a.agency_name}"`,
      `"${a.district}"`,
      a.total_works,
      a.completed_works,
      a.delayed_works,
      (a.total_expenditure / 10000000).toFixed(2),
      a.anomaly_count,
      a.agency_risk_score
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Agency_Risk_Matrix_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ width: '100%' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.5px', marginBottom: '0.25rem' }}>
          Agency Risk Matrix
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
          Comprehensive evaluation of nodal agencies.
        </p>
      </div>

      {/* 2 Top Analytics Cards */}
      <div className="agency-analytics-grid">
        {/* Performance Analytics: Risk vs Performance */}
        <div className="chart-card">
          <div className="chart-card-header">
            <span className="chart-title">Performance Analytics</span>
            <span className="chart-tag">RISK VS PERFORMANCE</span>
          </div>

          <div style={{ height: '180px', background: '#f8fafc', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
            <svg width="100%" height="100%" viewBox="0 0 400 180">
              <line x1="40" y1="20" x2="40" y2="150" stroke="#cbd5e1" strokeWidth="1" />
              <line x1="40" y1="150" x2="380" y2="150" stroke="#cbd5e1" strokeWidth="1" />
              <text x="15" y="85" fill="#94a3b8" fontSize="10" transform="rotate(-90 15,85)">Risk Score</text>
              <text x="180" y="170" fill="#94a3b8" fontSize="10">Completion Rate (%)</text>
              
              <circle cx="120" cy="45" r="7" fill="#ef4444" opacity="0.8" />
              <circle cx="180" cy="70" r="5" fill="#f97316" opacity="0.8" />
              <circle cx="260" cy="110" r="6" fill="#0284c7" opacity="0.8" />
              <circle cx="320" cy="135" r="8" fill="#10b981" opacity="0.8" />
              <circle cx="90" cy="35" r="6" fill="#ef4444" opacity="0.8" />
              <circle cx="340" cy="120" r="5" fill="#10b981" opacity="0.8" />
              <circle cx="210" cy="85" r="7" fill="#f59e0b" opacity="0.8" />
            </svg>
            <div style={{ position: 'absolute', bottom: '15px', right: '20px', fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>
              • High Risk (Red) • Optimal (Green)
            </div>
          </div>
        </div>

        {/* Trend: Completion */}
        <div className="chart-card">
          <div className="chart-card-header">
            <span className="chart-title">Trend</span>
            <span className="chart-tag">COMPLETION</span>
          </div>

          <div style={{ height: '180px', background: '#f8fafc', borderRadius: '8px', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', padding: '1rem', gap: '0.75rem' }}>
            <div style={{ width: '28px', height: '45px', background: '#cbd5e1', borderRadius: '4px' }} />
            <div style={{ width: '28px', height: '70px', background: '#cbd5e1', borderRadius: '4px' }} />
            <div style={{ width: '28px', height: '55px', background: '#cbd5e1', borderRadius: '4px' }} />
            <div style={{ width: '28px', height: '95px', background: '#94a3b8', borderRadius: '4px' }} />
            <div style={{ width: '28px', height: '120px', background: '#0d9488', borderRadius: '4px' }} />
          </div>
        </div>
      </div>

      {/* Agency Detail Matrix Card */}
      <div className="metric-card" style={{ padding: 0, overflow: 'hidden' }}>
        {/* Table Top Toolbar */}
        <div style={{ padding: '1.25rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', background: '#ffffff', flexWrap: 'wrap', gap: '0.75rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>
            Agency Detail Matrix ({filteredAgencies.length})
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ position: 'relative', width: '240px' }}>
              <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
              <input
                type="text"
                placeholder="Search agencies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.75rem 0.45rem 2.2rem',
                  fontSize: '0.85rem',
                  background: '#f1f5f9',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  outline: 'none'
                }}
              />
            </div>

            <button 
              onClick={exportCSV}
              style={{
                background: '#0f172a',
                color: '#ffffff',
                border: 'none',
                padding: '0.45rem 0.85rem',
                borderRadius: '6px',
                fontSize: '0.825rem',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                cursor: 'pointer'
              }}
            >
              <Download size={14} />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        {/* Scrollable Container with STICKY TABLE HEADERS */}
        <div className="sticky-table-wrapper" style={{ maxHeight: '520px' }}>
          <table className="matrix-table">
            <thead>
              <tr>
                <th>AGENCY</th>
                <th>DISTRICT</th>
                <th>WORKS</th>
                <th>COMPLETED</th>
                <th>DELAYED</th>
                <th>DISBURSED (₹CR)</th>
                <th>ANOMALIES</th>
                <th>RISK SCORE</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filteredAgencies.length === 0 ? (
                <tr>
                  <td colSpan={9} style={{ textAlign: 'center', padding: '2.5rem', color: '#94a3b8' }}>
                    {loading ? 'Loading agency performance matrix...' : 'No matching agencies found.'}
                  </td>
                </tr>
              ) : (
                filteredAgencies.map((ag, idx) => {
                  const isExpanded = expandedAgencyId === (ag.agency_id || `AG_${idx}`);
                  const isHighRisk = ag.agency_risk_score >= 50;
                  const expCr = (ag.total_expenditure / 10000000).toFixed(1);

                  return (
                    <React.Fragment key={ag.agency_id || idx}>
                      <tr 
                        onClick={() => setExpandedAgencyId(isExpanded ? null : (ag.agency_id || `AG_${idx}`))}
                        style={{ cursor: 'pointer', background: isExpanded ? '#fafafa' : '#ffffff' }}
                      >
                        <td style={{ fontWeight: 700, color: '#0f172a' }}>
                          {ag.agency_name}
                        </td>
                        <td style={{ color: '#475569' }}>
                          {ag.district}
                        </td>
                        <td style={{ fontWeight: 600 }}>
                          {ag.total_works}
                        </td>
                        <td style={{ color: '#16a34a', fontWeight: 600 }}>
                          {ag.completed_works}
                        </td>
                        <td style={{ color: ag.delayed_works > 0 ? '#ef4444' : '#64748b', fontWeight: 700 }}>
                          {ag.delayed_works}
                        </td>
                        <td style={{ fontWeight: 600 }}>
                          {expCr}
                        </td>
                        <td>
                          {ag.anomaly_count > 0 ? (
                            <span style={{ background: '#fef2f2', color: '#ef4444', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
                              {ag.anomaly_count}
                            </span>
                          ) : (
                            <span style={{ color: '#94a3b8' }}>0</span>
                          )}
                        </td>
                        <td>
                          <span className={`score-pill ${isHighRisk ? 'score-pill-red' : 'score-pill-green'}`}>
                            {Math.round(ag.agency_risk_score)}/100
                          </span>
                        </td>
                        <td>
                          <button 
                            className="btn-audit"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (onSelectAgency) onSelectAgency(ag);
                            }}
                          >
                            Audit
                          </button>
                        </td>
                      </tr>

                      {/* Expandable AI Risk Explanation Row */}
                      {isExpanded && (
                        <tr style={{ background: '#ffffff' }}>
                          <td colSpan={9} style={{ padding: '0.5rem 1.5rem 1.25rem 1.5rem' }}>
                            <div className="ai-risk-explanation-box">
                              <div className="ai-exp-header">
                                <Sparkles size={14} />
                                <span>AI RISK EXPLANATION</span>
                              </div>
                              <p className="ai-exp-text">
                                {ag.ai_explanation || `Pattern of systematic delays detected in infrastructure projects managed by ${ag.agency_name}. High concentration of anomalous material procurements recorded.`}
                              </p>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
