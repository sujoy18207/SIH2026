import React, { useState, useEffect } from 'react';
import { FileSpreadsheet, Search } from 'lucide-react';
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
    return (
      <div className="goi-card" style={{ padding: '2.5rem', textAlign: 'center', color: '#64748b' }}>
        Loading Official MP Allocation Database...
      </div>
    );
  }

  return (
    <div className="goi-card">
      <div className="goi-card-header">
        <div>
          <div className="goi-card-title">
            <FileSpreadsheet size={20} color="#0d9488" />
            Official MP Allocation Database (eSAKSHI Reference)
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.2rem' }}>
            Showing {filteredMps.length} Members of Parliament and constituency entitlement limits
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '260px' }}>
            <Search size={14} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
            <input
              type="text"
              placeholder="Search MP Name, Constituency..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="goi-input"
              style={{ paddingLeft: '2.2rem' }}
            />
          </div>

          <select
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="goi-select"
          >
            <option value="ALL">All States / UTs ({statesList.length})</option>
            {statesList.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="goi-table-container">
        <table className="goi-table">
          <thead>
            <tr>
              <th style={{ width: '70px' }}>Sr. No.</th>
              <th>Hon'ble Member of Parliament (MP)</th>
              <th>State / Union Territory</th>
              <th>Constituency</th>
              <th style={{ textAlign: 'right' }}>Allocated Limit Amount</th>
            </tr>
          </thead>
          <tbody>
            {filteredMps.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '2.5rem', color: '#94a3b8' }}>
                  No MP allocation records matching the filter.
                </td>
              </tr>
            ) : (
              filteredMps.slice(0, 100).map((m) => (
                <tr key={m.sr_no}>
                  <td style={{ fontWeight: 600, color: '#94a3b8' }}>#{m.sr_no}</td>
                  <td style={{ fontWeight: 700, color: '#0f2744' }}>{m.mp_name}</td>
                  <td>{m.state}</td>
                  <td style={{ fontWeight: 600, color: '#0284c7' }}>{m.constituency}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#16a34a' }}>
                    {formatCrores(m.allocated_amount)}
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
