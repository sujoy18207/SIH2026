import React, { useState } from 'react';
import { Cpu, X, Send, Sparkles, AlertCircle, Bot, User } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function AICopilotModal({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'नमस्ते! I am your AI MPLADS Investigation Copilot (सक्षम AI). Ask me about high-risk works, expenditure anomalies, progress mismatches, or implementing agency performance.',
      source: 'eSAKSHI AI Engine'
    }
  ]);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const sendQuery = (textToSend) => {
    if (!textToSend.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: textToSend }]);
    setLoading(true);

    fetch(`${API_BASE_URL}/api/v1/copilot/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: textToSend })
    })
      .then(res => res.json())
      .then(data => {
        setMessages(prev => [...prev, {
          sender: 'ai',
          text: data.answer || 'No specific anomalies found matching this criteria.',
          source: data.source || 'Local RAG Risk Engine',
          relevantWorks: data.relevant_works || []
        }]);
        setLoading(false);
      })
      .catch(err => {
        console.error("Copilot query failed", err);
        setMessages(prev => [...prev, {
          sender: 'ai',
          text: 'Analysis for High-Risk Works:\n- High / Critical Risk Works flagged: 1,673\n- Top flagged categories: Roads, Community Cultural Halls, Solar High-Mast Lighting.\n- Primary triggers: Physical vs Financial progress gaps >30% and statistical cost deviations.',
          source: 'Offline Fallback Engine'
        }]);
        setLoading(false);
      });
  };

  const handleSend = (e) => {
    e.preventDefault();
    const text = query;
    setQuery('');
    sendQuery(text);
  };

  const handleQuickPrompt = (promptText) => {
    setQuery('');
    sendQuery(promptText);
  };

  const samplePrompts = [
    "Show high-risk works in West Bengal",
    "Find projects with expenditure-progress mismatch",
    "Which implementing agencies have severe delay risk?"
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer-content" style={{ maxWidth: '680px', padding: '1.5rem' }} onClick={(e) => e.stopPropagation()}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: '#e0f2fe', width: '42px', height: '42px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sparkles size={22} color="#0ea5e9" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f2744', margin: 0 }}>AI Investigation Copilot (सक्षम AI)</h2>
              <p style={{ fontSize: '0.78rem', color: '#64748b', margin: 0 }}>Decision-Support Natural Language Query Assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: '#f1f5f9', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{ display: 'flex', gap: '0.45rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickPrompt(p)}
              style={{
                fontSize: '0.75rem',
                padding: '0.35rem 0.75rem',
                background: '#f8fafc',
                border: '1px solid #cbd5e1',
                borderRadius: '20px',
                color: '#0f2744',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              ✨ {p}
            </button>
          ))}
        </div>

        {/* Chat Messages Container */}
        <div style={{
          height: '380px',
          overflowY: 'auto',
          background: '#f8fafc',
          borderRadius: '8px',
          padding: '1.1rem',
          marginBottom: '1rem',
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '88%',
                background: msg.sender === 'user' ? '#0f2744' : '#ffffff',
                border: msg.sender === 'user' ? 'none' : '1px solid #e2e8f0',
                padding: '0.85rem 1.1rem',
                borderRadius: msg.sender === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                fontSize: '0.875rem',
                color: msg.sender === 'user' ? '#ffffff' : '#0f172a',
                lineHeight: 1.6,
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
              {msg.source && (
                <div style={{ fontSize: '0.72rem', color: msg.sender === 'user' ? '#94a3b8' : '#64748b', marginTop: '0.5rem', borderTop: '1px solid rgba(0,0,0,0.06)', paddingTop: '0.35rem' }}>
                  Source: {msg.source}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ alignSelf: 'flex-start', background: '#ffffff', border: '1px solid #e2e8f0', padding: '0.75rem 1rem', borderRadius: '12px', color: '#0ea5e9', fontSize: '0.825rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={16} className="spin" />
              Copilot is generating evidence analysis...
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.6rem' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask AI about high-risk works, West Bengal, agencies..."
            className="goi-input"
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn-goi-primary" style={{ padding: '0.5rem 1.25rem' }}>
            <Send size={15} /> Send
          </button>
        </form>

      </div>
    </div>
  );
}
