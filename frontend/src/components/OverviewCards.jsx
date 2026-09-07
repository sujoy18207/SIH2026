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
      <div className="kpi-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-title">Real eSAKSHI Works Monitored</div>
            <div className="kpi-value">{(stats.total_works || 0).toLocaleString('en-IN')}</div>
            <div className="kpi-sub">
              {(stats.completed_works_count || 0).toLocaleString('en-IN')} Completed • {stats.in_progress_works_count?.toLocaleString('en-IN')} In Progress • {stats.states_count} States/UTs
            </div>
          </div>
          <div style={{ background: '#e0f2fe', padding: '0.5rem', borderRadius: '4px' }}>
            <Layers size={20} color="#173a67" />
          </div>
        </div>
      </div>

      <div className="kpi-card warning">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-title">Total Vendor Disbursements (Real Ledger)</div>
            <div className="kpi-value">{formatCrores(stats.total_expenditure_amount)}</div>
            <div className="kpi-sub">
              Sanctioned: {formatCrores(stats.total_sanctioned_amount)} • {stats.vendors_count?.toLocaleString('en-IN')} Vendors
            </div>
          </div>
          <div style={{ background: '#fef3c7', padding: '0.5rem', borderRadius: '4px' }}>
            <IndianRupee size={20} color="#d97706" />
          </div>
        </div>
      </div>

      <div className="kpi-card critical">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-title">High / Critical Risk Anomalies</div>
            <div className="kpi-value" style={{ color: '#c53030' }}>
              {((stats.high_risk_works_count || 0) + (stats.critical_risk_works_count || 0)).toLocaleString('en-IN')}
            </div>
            <div className="kpi-sub" style={{ color: '#9b2c2c', fontWeight: 600 }}>
              {stats.critical_risk_works_count || 0} Priority Review Recommendations
            </div>
          </div>
          <div style={{ background: '#fff5f5', padding: '0.5rem', borderRadius: '4px' }}>
            <AlertTriangle size={20} color="#c53030" />
          </div>
        </div>
      </div>

      <div className="kpi-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-title">Duplicate Work Candidates</div>
            <div className="kpi-value" style={{ color: '#0284c7' }}>
              {(stats.duplicate_candidates_count || 0).toLocaleString('en-IN')}
            </div>
            <div className="kpi-sub">
              NLP Similarity Within Districts
            </div>
          </div>
          <div style={{ background: '#e0f2fe', padding: '0.5rem', borderRadius: '4px' }}>
            <Copy size={20} color="#0284c7" />
          </div>
        </div>
      </div>

      <div className="kpi-card success">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-title">Data Quality Index</div>
            <div className="kpi-value" style={{ color: '#15803d' }}>
              {stats.avg_data_quality_score || 95.0}%
            </div>
            <div className="kpi-sub">
              Data Completeness & Field Validity
            </div>
          </div>
          <div style={{ background: '#dcfce7', padding: '0.5rem', borderRadius: '4px' }}>
            <ShieldCheck size={20} color="#15803d" />
          </div>
        </div>
      </div>
    </div>
  );
}
