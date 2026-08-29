import React, { useState } from 'react';
import { Cpu, X, Send, Sparkles, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function AICopilotModal({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'नमस्ते! I am your AI MPLADS Investigation Copilot (सक्षम AI). Ask me about high-risk works, progress mismatches, or agency risk profiles.',
      sources: []
    }
  ]);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userText = query;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setQuery('');
    setLoading(true);

    fetch(`${API_BASE_URL}/api/v1/copilot/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userText })
    })
      .then(res => res.json())
      .then(data => {
        setMessages(prev => [...prev, {
          sender: 'ai',
          text: data.answer,
          source: data.source,
          relevantWorks: data.relevant_works || []
        }]);
        setLoading(false);
      })
      .catch(err => {
        setMessages(prev => [...prev, {
          sender: 'ai',
          text: 'Error retrieving evidence for query.',
          sources: []
        }]);
        setLoading(false);
      });
  };

  const samplePrompts = [
    "Show high-risk works in West Bengal",
    "Find projects with expenditure-progress mismatch",
    "Which implementing agencies have severe delay risk?"
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="drawer-content" style={{ maxWidth: '640px' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '2px solid var(--goi-navy)', pb: '0.8rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: '#e0f2fe', padding: '0.5rem', borderRadius: '4px' }}>
              <Cpu size={22} color="#002147" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--goi-navy)' }}>AI Investigation Copilot (सक्षम AI)</h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--goi-text-muted)' }}>Decision-Support Natural Language Query Assistant</p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => setQuery(p)}
              style={{
                fontSize: '0.75rem',
                padding: '0.25rem 0.6rem',
                background: '#f1f5f9',
                border: '1px solid #cbd5e1',
                borderRadius: '4px',
                color: '#002147',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              ✨ {p}
            </button>
          ))}
        </div>

        <div style={{
          height: '400px',
          overflowY: 'auto',
          background: '#f8fafc',
          borderRadius: '4px',
          padding: '1rem',
          marginBottom: '1rem',
          border: '1px solid var(--goi-border)',
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
                background: msg.sender === 'user' ? '#002147' : '#ffffff',
                border: '1px solid #cbd5e1',
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                color: msg.sender === 'user' ? '#ffffff' : '#1e293b',
                lineHeight: 1.5
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
              {msg.source && (
                <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.4rem', fontStyle: 'italic' }}>
                  Source: {msg.source}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ color: '#64748b', fontSize: '0.8rem', fontStyle: 'italic' }}>
              Copilot is generating evidence summary...
            </div>
          )}
        </div>

        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.6rem' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask AI about high-risk works, agencies..."
            style={{
              flex: 1,
              padding: '0.6rem',
              background: '#ffffff',
              border: '1px solid var(--goi-border)',
              borderRadius: '4px',
              color: '#1a252c',
              fontSize: '0.85rem'
            }}
          />
          <button type="submit" className="btn-goi-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Send size={14} /> Send
          </button>
        </form>
      </div>
    </div>
  );
}
