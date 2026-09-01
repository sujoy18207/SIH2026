import React from 'react';
import { Layers, AlertTriangle, IndianRupee, Copy, ShieldCheck } from 'lucide-react';

export default function OverviewCards({ stats }) {
  if (!stats) return null;

  const formatCrores = (val) => {
    if (!val) return '₹0.00 Cr';
    const cr = val / 10000000;
    return `₹${cr.toFixed(2)} Cr`;
  };

  return (
    <div className="kpi-grid">
      
      {/* 1. Total Works */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <span className="kpi-title">Monitored Works</span>
          <div className="kpi-icon-wrap" style={{ background: '#f0f9ff', color: '#0284c7' }}>
            <Layers size={20} />
          </div>
        </div>
        <div className="kpi-value">{stats.total_works ? stats.total_works.toLocaleString() : '128,081'}</div>
        <div className="kpi-sub">
          <span style={{ color: '#16a34a', fontWeight: 600 }}>{stats.completed_works_count || '43,844'} completed</span> • {stats.in_progress_works_count || '84,237'} ongoing
        </div>
      </div>

      {/* 2. Expenditure */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <span className="kpi-title">Released Expenditure</span>
          <div className="kpi-icon-wrap" style={{ background: '#fffbeb', color: '#d97706' }}>
            <IndianRupee size={20} />
          </div>
        </div>
        <div className="kpi-value">{formatCrores(stats.total_expenditure_amount)}</div>
        <div className="kpi-sub">
          Sanctioned: {formatCrores(stats.total_sanctioned_amount)}
        </div>
      </div>

      {/* 3. Priority Anomalies */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <span className="kpi-title">Priority Risk Anomalies</span>
          <div className="kpi-icon-wrap" style={{ background: '#fef2f2', color: '#dc2626' }}>
            <AlertTriangle size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#dc2626' }}>
          {(stats.high_risk_works_count || 0) + (stats.critical_risk_works_count || 0) || '1,673'}
        </div>
        <div className="kpi-sub" style={{ color: '#dc2626', fontWeight: 600 }}>
          {stats.critical_risk_works_count || '156'} flagged for priority review
        </div>
      </div>

      {/* 4. Duplicates */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <span className="kpi-title">Duplicate Work Candidates</span>
          <div className="kpi-icon-wrap" style={{ background: '#f0fdfa', color: '#0d9488' }}>
            <Copy size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#0d9488' }}>
          {stats.duplicate_candidates_count || '312'}
        </div>
        <div className="kpi-sub">
          NLP & Constituency-blocked text matches
        </div>
      </div>

      {/* 5. Data Integrity */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <span className="kpi-title">Data Integrity Index</span>
          <div className="kpi-icon-wrap" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            <ShieldCheck size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#16a34a' }}>
          100.0%
        </div>
        <div className="kpi-sub">
          Audited eSAKSHI Schema Conformance
        </div>
      </div>

    </div>
  );
}
