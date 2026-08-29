import React, { useState, useEffect } from 'react';
import { IndianRupee, Search, UserCheck, Award, FileSpreadsheet, MapPin } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function MPAllocatedLimitsTable() {
  const [mps, setMps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stateFilter, setStateFilter] = useState('ALL');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/mps/allocated-limits`)
      .then(res => res.json())
      .then(data => {
        setMps(data.mp_allocations || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load MP allocated limits database", err);
        setLoading(false);
      });
  }, []);

  const formatCrores = (val) => {
    if (!val) return '₹0.00 Cr';
    const cr = val / 10000000;
    return `₹${cr.toFixed(2)} Cr`;
  };

  const statesList = Array.from(new Set(mps.map(m => m.state))).sort();

  const filteredMps = mps.filter(m => {
    if (stateFilter !== 'ALL' && m.state !== stateFilter) return false;
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      const match = (
        m.mp_name.toLowerCase().includes(s) ||
        m.constituency.toLowerCase().includes(s) ||
        m.state.toLowerCase().includes(s)
      );
      if (!match) return false;
    }
    return true;
  });

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--goi-text-muted)' }}>Loading Official 543 MP Allocated Limit Database...</div>;
  }

  return (
    <div className="goi-card">
      <div className="goi-card-header">
        <div className="goi-card-title">
          <FileSpreadsheet size={22} color="var(--esakshi-teal)" />
          Official MP Allocation Database (eSAKSHI Reference Data)
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--goi-text-muted)', marginLeft: '0.5rem' }}>
            ({filteredMps.length} Hon'ble MPs Displayed)
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '260px' }}>
            <Search size={14} color="#6b7280" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search MP Name, Constituency..."
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
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            style={{
              padding: '0.4rem 0.75rem',
              background: '#ffffff',
              border: '1px solid var(--goi-border)',
              borderRadius: '4px',
              color: '#1a252c',
              fontSize: '0.825rem'
            }}
          >
            <option value="ALL">All States / UTs ({statesList.length})</option>
            {statesList.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="custom-table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Sr. No.</th>
              <th>Hon'ble Member of Parliament (MP)</th>
              <th>State / Union Territory</th>
              <th>Constituency</th>
              <th>Allocated Limit Amount (₹)</th>
            </tr>
          </thead>
          <tbody>
            {filteredMps.slice(0, 100).map((m) => (
              <tr key={m.sr_no}>
                <td style={{ fontWeight: 700, color: '#64748b', width: '60px' }}>{m.sr_no}</td>
                <td style={{ fontWeight: 700, color: '#002147' }}>{m.mp_name}</td>
                <td>{m.state}</td>
                <td style={{ fontWeight: 600, color: '#0284c7' }}>{m.constituency}</td>
                <td style={{ fontWeight: 800, color: '#15803d' }}>
                  {formatCrores(m.allocated_amount)}
                  <span style={{ fontSize: '0.72rem', color: '#64748b', marginLeft: '0.4rem', fontWeight: 500 }}>
                    (₹{m.allocated_amount.toLocaleString('en-IN')})
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
