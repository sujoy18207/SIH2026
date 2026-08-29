import React from 'react';

export default function AshokaStambhaLogo({ size = 52, style = {} }) {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', ...style }}>
      <img
        src="/ashoka_emblem.png"
        alt="State Emblem of India - Ashoka Stambha - Government of India"
        style={{
          height: `${size}px`,
          width: 'auto',
          objectFit: 'contain',
          display: 'block'
        }}
      />
    </div>
  );
}
