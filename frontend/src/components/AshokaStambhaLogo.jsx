import React from 'react';

export default function AshokaStambhaLogo({ size = 48, color = "#002147", showMotto = true }) {
  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Lion Capital Top Silhouette */}
        {/* Center Lion Head & Mane */}
        <path d="M50 8 C42 8 38 15 38 22 C38 28 42 34 50 36 C58 34 62 28 62 22 C62 15 58 8 50 8 Z" fill={color} />
        {/* Left Lion Profile */}
        <path d="M35 14 C28 14 24 20 24 28 C24 34 28 40 36 42 C33 36 33 28 35 14 Z" fill={color} opacity="0.9" />
        {/* Right Lion Profile */}
        <path d="M65 14 C72 14 76 20 76 28 C76 34 72 40 64 42 C67 36 67 28 65 14 Z" fill={color} opacity="0.9" />

        {/* Central Lion Chest & Pillars */}
        <path d="M36 36 L64 36 L68 56 L32 56 Z" fill={color} />

        {/* Abacus Base Bar */}
        <rect x="20" y="56" width="60" height="12" rx="2" fill={color} />

        {/* Ashoka Chakra Wheel (24 Spokes Wheel) */}
        <circle cx="50" cy="62" r="5" fill="#ffffff" stroke={color} strokeWidth="1.5" />
        <circle cx="50" cy="62" r="1.5" fill={color} />
        <line x1="50" y1="57" x2="50" y2="67" stroke={color} strokeWidth="1" />
        <line x1="45" y1="62" x2="55" y2="62" stroke={color} strokeWidth="1" />
        <line x1="46.5" y1="58.5" x2="53.5" y2="65.5" stroke={color} strokeWidth="0.8" />
        <line x1="46.5" y1="65.5" x2="53.5" y2="58.5" stroke={color} strokeWidth="0.8" />

        {/* Left Horse / Right Bull symbols on Abacus */}
        <circle cx="28" cy="62" r="2.5" fill="#ffffff" />
        <circle cx="72" cy="62" r="2.5" fill="#ffffff" />

        {/* Bell-shaped Lotus Base */}
        <path d="M26 68 C32 82 68 82 74 68 Z" fill={color} />

        {/* Bottom Pedestal Base */}
        <rect x="22" y="82" width="56" height="5" rx="1.5" fill={color} />
      </svg>

      {showMotto && (
        <span style={{
          fontFamily: "'Mukta', 'Devanagari', sans-serif",
          fontSize: size > 40 ? '0.65rem' : '0.55rem',
          fontWeight: 800,
          color: color,
          letterSpacing: '0.5px',
          marginTop: '-4px',
          whiteSpace: 'nowrap'
        }}>
          सत्यमेव जयते
        </span>
      )}
    </div>
  );
}
