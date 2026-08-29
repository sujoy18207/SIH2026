import React, { useState } from 'react';
import { X, RefreshCw, User, Lock, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import AshokaStambhaLogo from './AshokaStambhaLogo';

export default function LoginModal({ isOpen, onClose, onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState('7x2fm');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const generateNewCaptcha = () => {
    const chars = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ';
    let code = '';
    for (let i = 0; i < 5; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptchaCode(code);
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (captchaInput.trim().toLowerCase() !== captchaCode.toLowerCase()) {
      setErrorMsg('Invalid Captcha. Please enter the captcha code displayed.');
      return;
    }
    setErrorMsg('');
    if (onLoginSuccess) onLoginSuccess(username || 'Officer Admin');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div
        className="login-split-card"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '90%',
          maxWidth: '850px',
          height: '540px',
          background: '#ffffff',
          borderRadius: '12px',
          overflow: 'hidden',
          display: 'flex',
          boxShadow: '0 20px 50px rgba(0,0,0,0.3)',
          position: 'relative'
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            right: '15px',
            top: '15px',
            background: '#f1f5f9',
            border: 'none',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            cursor: 'pointer',
            zIndex: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <X size={18} color="#475569" />
        </button>

        {/* Left Side: Dark Hero Image Overlay */}
        <div
          style={{
            flex: 1,
            backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), url(/parliament_hero_bg.png)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            padding: '3rem 2rem',
            color: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            justify: 'flex-end'
          }}
        >
          <h1 style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '1px', marginBottom: '0.2rem' }}>
            eSAKSHI
          </h1>
          <p style={{ fontSize: '1rem', color: '#cbd5e1', fontWeight: 500 }}>
            SAnsad sadasya sthaniya KSHetra vIkas yojana
          </p>
          <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.2)', fontSize: '0.78rem', color: '#94a3b8' }}>
            Ministry of Statistics and Programme Implementation • Government of India
          </div>
        </div>

        {/* Right Side: Official Login Form */}
        <div style={{ flex: 1, padding: '2.5rem 2rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {/* Header Emblem */}
          <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
              <AshokaStambhaLogo size={42} color="#002147" showMotto={true} />
              <div style={{ textTransform: 'uppercase', fontSize: '0.65rem', fontWeight: 800, color: '#002147', textAlign: 'left', lineHeight: 1.25 }}>
                Government of India<br />
                <span style={{ color: '#475569', fontWeight: 600 }}>Ministry of Statistics & Programme Implementation</span>
              </div>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#002147' }}>Log In</h2>
          </div>

          {errorMsg && (
            <div style={{ padding: '0.4rem 0.6rem', background: '#fee2e2', border: '1px solid #f87171', borderRadius: '4px', color: '#991b1b', fontSize: '0.78rem', marginBottom: '0.75rem', textAlign: 'center' }}>
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '0.85rem', position: 'relative' }}>
              <User size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                style={{
                  width: '100%',
                  padding: '0.6rem 0.6rem 0.6rem 2.4rem',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  color: '#0f172a'
                }}
              />
            </div>

            <div style={{ marginBottom: '0.5rem', position: 'relative' }}>
              <Lock size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                style={{
                  width: '100%',
                  padding: '0.6rem 2.4rem 0.6rem 2.4rem',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  color: '#0f172a'
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{ position: 'absolute', right: '12px', top: '12px', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            <div style={{ textAlign: 'right', marginBottom: '0.85rem' }}>
              <a href="#" onClick={(e) => { e.preventDefault(); alert("Please contact District Administration / MoSPI admin for password reset."); }} style={{ fontSize: '0.75rem', color: '#0284c7', fontWeight: 600, textDecoration: 'none' }}>
                Forgot Password?
              </a>
            </div>

            {/* Captcha Box */}
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{
                background: '#e2e8f0',
                border: '1px solid #94a3b8',
                borderRadius: '4px',
                padding: '0.4rem 0.8rem',
                fontFamily: 'monospace',
                fontWeight: 800,
                fontSize: '1.1rem',
                letterSpacing: '3px',
                color: '#0f172a',
                textDecoration: 'line-through',
                userSelect: 'none'
              }}>
                {captchaCode}
              </div>
              <button
                type="button"
                onClick={generateNewCaptcha}
                title="Refresh Captcha"
                style={{ background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', padding: '0.5rem', cursor: 'pointer' }}
              >
                <RefreshCw size={14} color="#475569" />
              </button>
              <input
                type="text"
                required
                value={captchaInput}
                onChange={(e) => setCaptchaInput(e.target.value)}
                placeholder="Captcha"
                style={{
                  flex: 1,
                  padding: '0.55rem',
                  border: '1px solid #cbd5e1',
                  borderRadius: '4px',
                  fontSize: '0.85rem'
                }}
              />
            </div>

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '0.7rem',
                background: '#0091ff',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.9rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
            >
              Login
            </button>
          </form>

          <p style={{ fontSize: '0.7rem', color: '#ef4444', marginTop: '0.85rem', textAlign: 'center', lineHeight: 1.3 }}>
            If the OTP is not received via SMS, please check your registered email inbox for the OTP.
          </p>

          <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.68rem', color: '#94a3b8' }}>
            Copyright © 2026 Tata Consultancy Services Limited / MoSPI. All Rights Reserved
          </div>
        </div>
      </div>
    </div>
  );
}
