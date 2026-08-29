import React, { useState, useEffect } from 'react';
import { Building2, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

export default function AgencyRiskMatrix() {
  const [agencies, setAgencies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/agencies')
      .then(res => res.json())
      .then(data => {
        setAgencies(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load agencies", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: '1.5rem', color: 'var(--goi-text-muted)' }}>Loading Agency Performance Matrix...</div>;

  return (
    <div className="goi-card">
      <div className="goi-card-header">
        <div className="goi-card-title">
          <Building2 size={20} color="#002147" />
          Headline Feature — Executing Agency Multi-Project Performance Matrix
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--goi-text-muted)', marginLeft: '0.5rem' }}>
            ({agencies.length} Designated Agencies Monitored)
          </span>
        </div>
      </div>

      <div className="custom-table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Executing Agency Name</th>
              <th>District</th>
              <th>Total Works</th>
              <th>Completed Works</th>
              <th>Delayed Works</th>
              <th>Total Expenditure</th>
              <th>Anomaly Count</th>
              <th>Agency Risk Profile</th>
            </tr>
          </thead>
          <tbody>
            {agencies.sort((a, b) => b.agency_risk_score - a.agency_risk_score).map((ag) => (
              <tr key={ag.agency_id}>
                <td style={{ fontWeight: 700, color: '#002147' }}>{ag.agency_name}</td>
                <td>{ag.district}</td>
                <td>{ag.total_works}</td>
                <td style={{ color: '#15803d', fontWeight: 600 }}>{ag.completed_works}</td>
                <td style={{ color: ag.delayed_works > 0 ? '#c53030' : '#64748b', fontWeight: 600 }}>{ag.delayed_works}</td>
                <td>₹{(ag.total_expenditure / 100000).toFixed(2)} Lakhs</td>
                <td style={{ fontWeight: 700, color: ag.anomaly_count > 0 ? '#d97706' : '#64748b' }}>{ag.anomaly_count}</td>
                <td>
                  <span className={`badge-risk ${ag.agency_risk_level.toLowerCase()}`}>
                    {ag.agency_risk_score.toFixed(0)} • {ag.agency_risk_level} Risk
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
