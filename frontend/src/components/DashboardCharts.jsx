import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid
} from 'recharts';
import { PieChart as PieIcon, Activity, MapPin } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

const RISK_COLORS = {
  Critical: '#991b1b',
  High: '#c2410c',
  Medium: '#854d0e',
  Low: '#166534',
};

const STATUS_COLORS = {
  'Pending Sanction': '#a16207',
  'Sanctioned': '#0369a1',
  'In Progress': '#6d28d9',
  'Completed': '#15803d',
};

const fmtIN = (v) => (v == null ? '0' : v.toLocaleString('en-IN'));

/**
 * Real-data dashboard charts over the eSAKSHI dataset:
 *  1. National risk-level distribution (donut)    — /api/v1/overview
 *  2. Work pipeline status (bar)                  — /api/v1/overview
 *  3. Top 10 states by high-risk flags (bar)      — /api/v1/geo/risk-zones
 */
export default function DashboardCharts({ stats }) {
  const [zones, setZones] = useState(null);
  const [zonesError, setZonesError] = useState(null);

  // State-level aggregates for the top-states chart
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/geo/risk-zones`)
      .then(res => {
        if (!res.ok) throw new Error(`geo/risk-zones returned ${res.status}`);
        return res.json();
      })
      .then(data => setZones(data.zones || []))
      .catch(err => {
        console.error('Failed to load geo risk zones for charts', err);
        setZonesError(err.message);
      });
  }, []);

  if (!stats) return null;

  const s = stats;

  // ---- chart 1: risk-level distribution (full DB counts, not the fetched page) ----
  const riskData = [
    { name: 'Critical', value: s.critical_risk_works_count || 0 },
    { name: 'High', value: s.high_risk_works_count || 0 },
    { name: 'Medium', value: s.medium_risk_works_count || 0 },
    { name: 'Low', value: s.low_risk_works_count || 0 },
  ].filter(d => d.value > 0);

  // ---- chart 2: work pipeline status ----
  const pipelineData = [
    { name: 'Pending Sanction', value: s.pending_sanction_works_count || 0 },
    { name: 'Sanctioned', value: s.sanctioned_works_count || 0 },
    { name: 'In Progress', value: s.in_progress_works_count || 0 },
    { name: 'Completed', value: s.completed_works_count || 0 },
  ];

  // ---- chart 3: top states by high-risk works ----
  const topStates = (zones || [])
    .slice()
    .sort((a, b) => (b.high_risk_works || 0) - (a.high_risk_works || 0))
    .slice(0, 10)
    .map(z => ({ name: z.state, high_risk: z.high_risk_works }));

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
      {/* Chart 1: Risk-level distribution donut */}
      <div className="goi-card" style={{ padding: '1rem 1.25rem 0.5rem' }}>
        <div className="goi-card-title" style={{ fontSize: '0.95rem' }}>
          <PieIcon size={18} color="#173a67" />
          National Risk Distribution
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--goi-text-muted)', marginLeft: 'auto' }}>
            All {fmtIN(s.total_works)} monitored works
          </span>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={riskData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={2}
              stroke="#ffffff"
              strokeWidth={2}
            >
              {riskData.map(d => (
                <Cell key={d.name} fill={RISK_COLORS[d.name]} />
              ))}
            </Pie>
            <Tooltip formatter={fmtIN} />
            <Legend formatter={(value) => `${value}`} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 2: Work pipeline status */}
      <div className="goi-card" style={{ padding: '1rem 1.25rem 0.5rem' }}>
        <div className="goi-card-title" style={{ fontSize: '0.95rem' }}>
          <Activity size={18} color="#173a67" />
          Work Pipeline Status
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--goi-text-muted)', marginLeft: 'auto' }}>
            {fmtIN(s.total_works)} works
          </span>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={pipelineData} margin={{ top: 15, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#475569' }} />
            <YAxis tick={{ fontSize: 11, fill: '#475569' }} tickFormatter={fmtIN} />
            <Tooltip formatter={fmtIN} />
            <Bar dataKey="value" name="Works" radius={[4, 4, 0, 0]}>
              {pipelineData.map(d => (
                <Cell key={d.name} fill={STATUS_COLORS[d.name] || '#0369a1'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 3: Top states by high-risk flags */}
      <div className="goi-card" style={{ padding: '1rem 1.25rem 0.5rem' }}>
        <div className="goi-card-title" style={{ fontSize: '0.95rem' }}>
          <MapPin size={18} color="#173a67" />
          Top 10 States by High-Risk Flags
        </div>
        {zonesError ? (
          <div style={{ color: 'var(--risk-critical)', fontSize: '0.8rem', padding: '2rem 0', textAlign: 'center' }}>
            Failed to load state data: {zonesError}
          </div>
        ) : zones === null ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '2rem 0', textAlign: 'center' }}>
            Loading state risk aggregates from the eSAKSHI database...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={topStates} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#475569' }} tickFormatter={fmtIN} />
              <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 10.5, fill: '#475569' }} />
              <Tooltip formatter={fmtIN} />
              <Bar dataKey="high_risk" name="High-Risk Works" fill="#c2410c" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
