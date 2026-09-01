import React, { useState, useEffect } from 'react';
import { Building2 } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function AgencyRiskMatrix() {
  const [agencies, setAgencies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/agencies`)
      .then(res => res.json())
      .then(data => {
        setAgencies(data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load agencies", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="goi-card" style={{ padding: '2.5rem', textAlign: 'center', color: '#64748b' }}>
        Loading Agency Multi-Project Performance Matrix...
      </div>
    );
  }

  return (
    <div className="goi-card">
      <div className="goi-card-header">
        <div>
          <div className="goi-card-title">
            <Building2 size={20} color="#0d9488" />
            Executing Agency Risk & Performance Matrix
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.2rem' }}>
            Monitoring {agencies.length} designated executing agencies and district authorities across India
          </div>
        </div>
      </div>

      <div className="goi-table-container">
        <table className="goi-table">
          <thead>
            <tr>
              <th>Executing Agency</th>
              <th>District / State</th>
              <th>Total Works</th>
              <th>Completed</th>
              <th>Delayed</th>
              <th>Disbursed Total</th>
              <th>Anomaly Count</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {agencies.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '2.5rem', color: '#94a3b8' }}>
                  No agency records available.
                </td>
              </tr>
            ) : (
              agencies.sort((a, b) => b.agency_risk_score - a.agency_risk_score).map((ag) => (
                <tr key={ag.agency_id}>
                  <td style={{ fontWeight: 700, color: '#0f2744' }}>{ag.agency_name}</td>
                  <td>{ag.district}</td>
                  <td>{ag.total_works}</td>
                  <td style={{ color: '#16a34a', fontWeight: 600 }}>{ag.completed_works}</td>
                  <td style={{ color: ag.delayed_works > 0 ? '#dc2626' : '#64748b', fontWeight: 600 }}>{ag.delayed_works}</td>
                  <td style={{ fontWeight: 600 }}>₹{(ag.total_expenditure / 100000).toFixed(2)} L</td>
                  <td style={{ fontWeight: 700, color: ag.anomaly_count > 0 ? '#ea580c' : '#64748b' }}>{ag.anomaly_count}</td>
                  <td>
                    <span className={`badge-risk ${ag.agency_risk_level.toLowerCase()}`}>
                      {ag.agency_risk_score.toFixed(0)} • {ag.agency_risk_level}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
