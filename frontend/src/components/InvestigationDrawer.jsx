import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, CheckCircle2, AlertOctagon, MapPin, Copy, Clock, FileText, UserCheck, Send, ShieldCheck, Database, Building2 } from 'lucide-react';

export default function InvestigationDrawer({ workId, onClose, onSubmitReview }) {
  const [dossier, setDossier] = useState(null);
  const [loading, setLoading] = useState(true);

  // Review Form State
  const [officerName, setOfficerName] = useState('District Magistrate Nadia');
  const [officerRole, setOfficerRole] = useState('District Collector');
  const [reviewAction, setReviewAction] = useState('Escalated for Physical Site Inspection');
  const [remarks, setRemarks] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

  useEffect(() => {
    if (!workId) return;
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/works/${workId}/investigation`)
      .then(res => res.json())
      .then(data => {
        setDossier(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load dossier", err);
        setLoading(false);
      });
  }, [workId]);

  if (!workId) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!dossier || !dossier.alert) return;

    setIsSubmitting(true);
    const alertId = dossier.alert.alert_id;

    fetch(`http://localhost:8000/api/v1/alerts/${alertId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        officer_name: officerName,
        officer_role: officerRole,
        action: reviewAction,
        remarks: remarks
      })
    })
      .then(res => res.json())
      .then(resData => {
        setIsSubmitting(false);
        setSubmitMessage("✅ Officer Action Submitted! Recorded in immutable official audit trail.");
        if (onSubmitReview) onSubmitReview(alertId);
      })
      .catch(err => {
        setIsSubmitting(false);
        setSubmitMessage("❌ Failed to submit review.");
      });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <p style={{ color: 'var(--goi-text-muted)' }}>Loading Official Case Investigation Dossier...</p>
          </div>
        ) : !dossier || !dossier.work ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <p style={{ color: 'var(--risk-critical)' }}>Work Dossier Not Found.</p>
            <button className="btn-goi-primary" onClick={onClose} style={{ marginTop: '1rem' }}>Close</button>
          </div>
        ) : (
          <div>
            {/* Official Header */}
            <div style={{
              borderBottom: '2px solid var(--goi-navy)',
              paddingBottom: '1rem',
              marginBottom: '1.25rem',
              display: 'flex',
              justify: 'space-between',
              alignItems: 'flex-start'
            }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--goi-saffron)', fontWeight: 800, letterSpacing: '0.5px' }}>
                  GOVERNMENT OF INDIA • OFFICIAL CASE DOSSIER
                </div>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--goi-navy)', margin: '0.2rem 0' }}>
                  {dossier.work.work_id}
                </h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--goi-text-muted)' }}>
                  {dossier.work.work_category} • {dossier.work.district}, {dossier.work.state} ({dossier.work.constituency})
                </div>
              </div>
              <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer' }}>
                <X size={22} />
              </button>
            </div>

            {/* Risk, Confidence & Data Quality Summary */}
            {dossier.alert && (
              <div style={{
                background: '#fff5f5',
                border: '1px solid #feb2b2',
                borderLeft: '4px solid var(--risk-critical)',
                borderRadius: '4px',
                padding: '1rem',
                marginBottom: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ShieldAlert size={20} color="#c53030" />
                    <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#9b2c2c' }}>
                      Overall Risk Score: {dossier.alert.risk_score} / 100 ({dossier.alert.risk_level} Risk)
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: '#742a2a', fontWeight: 600 }}>Ref: {dossier.alert.alert_id}</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.6rem', marginTop: '0.6rem' }}>
                  <div style={{ background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.68rem', color: '#64748b' }}>EVIDENCE CONFIDENCE</div>
                    <div style={{ fontWeight: 800, color: '#1e40af' }}>{dossier.alert.evidence_confidence_score?.toFixed(0)}%</div>
                  </div>
                  <div style={{ background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.68rem', color: '#64748b' }}>DATA QUALITY INDEX</div>
                    <div style={{ fontWeight: 800, color: dossier.alert.data_quality_score < 70 ? '#d97706' : '#15803d' }}>
                      {dossier.alert.data_quality_score?.toFixed(0)}%
                    </div>
                  </div>
                  <div style={{ background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.68rem', color: '#64748b' }}>DUPLICATE RISK</div>
                    <div style={{ fontWeight: 800, color: '#0284c7' }}>{dossier.alert.risk_breakdown.duplicate_risk_score}%</div>
                  </div>
                </div>
              </div>
            )}

            {/* Work Details Panel */}
            <div style={{ background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', padding: '1rem', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.6rem', color: 'var(--goi-navy)' }}>
                Work Project Details & Milestone Financials
              </h3>
              <p style={{ fontSize: '0.88rem', marginBottom: '0.8rem', color: '#334155', background: '#f8fafc', padding: '0.6rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                "{dossier.work.work_description}"
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', marginBottom: '0.8rem', fontSize: '0.825rem' }}>
                <div><span style={{ color: '#64748b' }}>Hon'ble MP:</span> <strong>{dossier.work.mp_name}</strong></div>
                <div><span style={{ color: '#64748b' }}>Executing Agency:</span> <strong>{dossier.work.implementing_agency_name}</strong></div>
                <div><span style={{ color: '#64748b' }}>Sanctioned Cost:</span> <strong>₹{(dossier.work.sanctioned_amount / 100000).toFixed(2)} Lakhs</strong></div>
                <div><span style={{ color: '#64748b' }}>Released Payment:</span> <strong>₹{(dossier.work.expenditure / 100000).toFixed(2)} Lakhs</strong></div>
              </div>

              {/* Progress gap */}
              <div style={{ marginTop: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.2rem' }}>
                  <span>Physical Completion: <strong>{dossier.work.physical_progress_pct}%</strong></span>
                  <span>Financial Progress: <strong>{dossier.work.financial_progress_pct}%</strong></span>
                </div>

                <div className="progress-bar-container" style={{ height: '8px', marginBottom: '0.3rem' }}>
                  <div className="progress-bar-fill progress-fill-physical" style={{ width: `${dossier.work.physical_progress_pct}%`, position: 'absolute' }} />
                  <div className="progress-bar-fill progress-fill-financial" style={{ width: `${dossier.work.financial_progress_pct}%`, opacity: 0.6 }} />
                </div>
              </div>
            </div>

            {/* Headline Feature: Agency Multi-Project Pattern History */}
            {dossier.agency_profile && (
              <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderLeft: '4px solid #0284c7', borderRadius: '4px', padding: '0.85rem', marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '0.825rem', fontWeight: 700, color: '#0369a1', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Building2 size={16} /> Agency Multi-Project Execution Pattern ({dossier.agency_profile.agency_name})
                </h4>
                <div style={{ fontSize: '0.8rem', color: '#0f172a' }}>
                  Agency manages <strong>{dossier.agency_profile.total_works} works</strong> in district ({dossier.agency_profile.delayed_works} delayed, {dossier.agency_profile.anomaly_count} total anomaly signals). Agency Risk Score: <strong>{dossier.agency_profile.agency_risk_score} / 100</strong>.
                </div>
              </div>
            )}

            {/* Candidate Duplicate Work Match */}
            {dossier.duplicate_candidate_work && (
              <div style={{ background: '#fffbebfb', border: '1px solid #fde68a', borderLeft: '4px solid #d97706', borderRadius: '4px', padding: '0.85rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem', color: '#b45309', fontWeight: 700, fontSize: '0.85rem' }}>
                  <Copy size={16} /> Potentially Similar/Duplicate Work — Verification Required
                </div>
                <div style={{ fontSize: '0.825rem', color: '#451a03' }}>
                  High text similarity detected with candidate work <strong>{dossier.duplicate_candidate_work.work_id}</strong> (Duplicate Risk Score: {dossier.alert.duplicate_risk_score}%).
                </div>
                <div style={{ fontSize: '0.78rem', color: '#78350f', marginTop: '0.4rem', background: '#ffffff', padding: '0.5rem', borderRadius: '4px', border: '1px solid #fef3c7' }}>
                  <strong>Candidate Description:</strong> "{dossier.duplicate_candidate_work.work_description}"
                </div>
              </div>
            )}

            {/* AI Evidence Narrative */}
            {dossier.alert && (
              <div style={{ background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', padding: '1rem', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.6rem', color: 'var(--goi-navy)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <FileText size={16} /> Evidence Summary & Recommended Action
                </h3>
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'inherit',
                  fontSize: '0.8rem',
                  color: '#334155',
                  lineHeight: 1.55,
                  background: '#f8fafc',
                  padding: '0.75rem',
                  borderRadius: '4px',
                  border: '1px solid #e2e8f0'
                }}>
                  {dossier.alert.narrative_explanation}
                </pre>
              </div>
            )}

            {/* Official Review & Append-Only Audit Trail Form */}
            <div style={{ background: '#f8fafc', border: '1px solid var(--goi-navy)', borderRadius: '4px', padding: '1rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.8rem', color: 'var(--goi-navy)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <UserCheck size={16} /> Officer Verification & Append-Only Audit Action
              </h3>

              {submitMessage && (
                <div style={{ padding: '0.5rem', background: '#f0fff4', border: '1px solid #16a34a', borderRadius: '4px', color: '#15803d', fontSize: '0.8rem', marginBottom: '0.8rem' }}>
                  {submitMessage}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#475569', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>Officer Name</label>
                    <input
                      type="text"
                      value={officerName}
                      onChange={(e) => setOfficerName(e.target.value)}
                      required
                      style={{ width: '100%', padding: '0.4rem', background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#475569', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>Officer Role / Designation</label>
                    <input
                      type="text"
                      value={officerRole}
                      onChange={(e) => setOfficerRole(e.target.value)}
                      required
                      style={{ width: '100%', padding: '0.4rem', background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '0.75rem' }}>
                  <label style={{ fontSize: '0.75rem', color: '#475569', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>Official Action Taken</label>
                  <select
                    value={reviewAction}
                    onChange={(e) => setReviewAction(e.target.value)}
                    style={{ width: '100%', padding: '0.4rem', background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  >
                    <option value="Escalated for Physical Site Inspection">Escalated for Physical Site Inspection</option>
                    <option value="Verified Valid (No Fraud Found)">Verified Valid (No Fraud Found)</option>
                    <option value="Mark as False Positive Anomaly">Mark as False Positive Anomaly</option>
                    <option value="Closed with Show-Cause Notice to Agency">Closed with Show-Cause Notice to Agency</option>
                  </select>
                </div>

                <div style={{ marginBottom: '0.75rem' }}>
                  <label style={{ fontSize: '0.75rem', color: '#475569', display: 'block', marginBottom: '0.2rem', fontWeight: 600 }}>Official Audit Remarks</label>
                  <textarea
                    rows={3}
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    placeholder="Enter official administrative audit remarks..."
                    required
                    style={{ width: '100%', padding: '0.4rem', background: '#ffffff', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-goi-primary"
                  style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.4rem' }}
                >
                  <Send size={14} />
                  {isSubmitting ? 'Recording Audit Action...' : 'Record Action in Immutable Audit Log'}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
