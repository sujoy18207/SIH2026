import React, { useState, useEffect } from 'react';
import { X, Send, FileText, CheckCircle2, User, MapPin, Building, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function CitizenRequestModal({ isOpen, onClose }) {
  const [submitted, setSubmitted] = useState(false);
  const [mps, setMps] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    mobile: '',
    state: '',
    locationType: 'rural',
    subDistrict: '',
    mpName: '',
    workTitle: '',
    workDescription: '',
    fundRequired: ''
  });

  // Load real MP allocations (Lok Sabha + Rajya Sabha) from the eSAKSHI dataset
  useEffect(() => {
    if (!isOpen || mps.length > 0) return;
    fetch(`${API_BASE_URL}/api/v1/mps/allocated-limits?house=Lok%20Sabha&limit=1000`)
      .then(res => res.json())
      .then(data => setMps(data.mp_allocations || []))
      .catch(err => console.error("Failed to load MP list", err));
  }, [isOpen, mps.length]);

  if (!isOpen) return null;

  const statesList = Array.from(new Set(mps.map(m => m.state))).sort();

  const stateMps = formData.state
    ? mps.filter(m => m.state === formData.state)
    : [];

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  const handleReset = () => {
    setSubmitted(false);
    setFormData({
      name: '',
      email: '',
      mobile: '',
      state: '',
      locationType: 'rural',
      subDistrict: '',
      mpName: '',
      workTitle: '',
      workDescription: '',
      fundRequired: ''
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer-content" style={{ maxWidth: '680px' }} onClick={(e) => e.stopPropagation()}>
        <div style={{
          borderBottom: '2px solid var(--esakshi-teal)',
          paddingBottom: '0.85rem',
          marginBottom: '1.25rem',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--esakshi-teal)', letterSpacing: '0.5px' }}>
              MPLADS e-SAKSHI CITIZEN PORTAL
            </span>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--goi-navy)', margin: '0.1rem 0' }}>
              Submit Citizen Work Request
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#64748b' }}>
              Propose local community development needs directly to your Member of Parliament
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {submitted ? (
          <div style={{ padding: '2rem', textAlign: 'center', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px' }}>
            <CheckCircle2 size={48} color="#166534" style={{ margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#166534', marginBottom: '0.5rem' }}>
              Citizen Request Submitted Successfully!
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#334155', marginBottom: '1rem' }}>
              Reference ID: <strong>CIT-MPLADS-2026-88942</strong>
            </p>
            <p style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '1.5rem' }}>
              Your request for <strong>"{formData.workTitle || 'Local Infrastructure Request'}"</strong> has been queued in the eSAKSHI citizen workflow for review by {formData.mpName}.
            </p>
            <button className="btn-esakshi-teal" onClick={handleReset}>Submit Another Request</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {/* User Details */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--goi-navy)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <User size={16} color="var(--esakshi-teal)" /> 1. Citizen Personal Details
              </h4>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Full Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter your full name"
                    style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Mobile Number *</label>
                  <input
                    type="tel"
                    required
                    maxLength={10}
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                    placeholder="10-digit Mobile Number"
                    style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Email Address (Optional)</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="name@example.com"
                  style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                />
              </div>
            </div>

            {/* Work Location Details */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--goi-navy)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <MapPin size={16} color="var(--esakshi-teal)" /> 2. Work Location & MP Representative
              </h4>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>State / UT *</label>
                  <select
                    required
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value, mpName: '' })}
                    style={{ width: '100%', padding: '0.4rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  >
                    <option value="">Select State / Union Territory...</option>
                    {statesList.map(st => (
                      <option key={st} value={st}>{st}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Sub-District / Block / Village Area</label>
                  <input
                    type="text"
                    value={formData.subDistrict}
                    onChange={(e) => setFormData({ ...formData, subDistrict: e.target.value })}
                    placeholder="e.g. Krishnanagar Block"
                    style={{ width: '100%', padding: '0.4rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Select Hon'ble Member of Parliament (MP) *</label>
                <select
                  required
                  value={formData.mpName}
                  onChange={(e) => setFormData({ ...formData, mpName: e.target.value })}
                  disabled={!formData.state}
                  style={{ width: '100%', padding: '0.4rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem', fontWeight: 600, color: '#002147' }}
                >
                  <option value="">{formData.state ? 'Select your MP...' : 'Select a State first...'}</option>
                  {stateMps.map(m => (
                    <option key={m.sr_no} value={`Hon'ble ${m.mp_name} (${m.constituency} Constituency)`}>
                      Hon'ble {m.mp_name} — {m.constituency}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Proposed Work Details */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '1.25rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--goi-navy)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Building size={16} color="var(--esakshi-teal)" /> 3. Proposed Work Description & Fund Estimate
              </h4>

              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Work Title *</label>
                <input
                  type="text"
                  required
                  value={formData.workTitle}
                  onChange={(e) => setFormData({ ...formData, workTitle: e.target.value })}
                  placeholder="e.g. Installation of Solar Street Lights in Village Ward 4"
                  style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                />
              </div>

              <div style={{ marginBottom: '0.75rem' }}>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Work Description & Locality Need *</label>
                <textarea
                  rows={3}
                  required
                  value={formData.workDescription}
                  onChange={(e) => setFormData({ ...formData, workDescription: e.target.value })}
                  placeholder="Provide details of the locality requirement and public community benefit..."
                  style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Approximate Fund Required (in ₹ Lakhs)</label>
                <input
                  type="number"
                  step="0.5"
                  value={formData.fundRequired}
                  onChange={(e) => setFormData({ ...formData, fundRequired: e.target.value })}
                  placeholder="e.g. 5.5"
                  style={{ width: '100%', padding: '0.4rem 0.6rem', border: '1px solid var(--goi-border)', borderRadius: '4px', fontSize: '0.825rem' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button type="button" className="btn-esakshi-outline" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn-esakshi-teal" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Send size={14} /> Submit Citizen Request
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
