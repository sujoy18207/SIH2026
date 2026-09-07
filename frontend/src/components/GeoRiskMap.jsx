import React, { useState, useEffect, useMemo } from 'react';
import {
  Search,
  Sparkles,
  Navigation
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import { API_BASE_URL } from '../apiConfig';

/**
 * Map tile configuration.
 *
 * The default tile provider is configurable via environment variables so a
 * self-hosted / commercial / CDN tile server can be swapped in without code
 * changes. OpenStreetMap's public tile server is for light and development
 * usage only; it is NOT unlimited, so point VITE_MAP_TILE_URL at a dedicated
 * provider before high-traffic production use.
 */
const TILE_LAYERS = {
  street: {
    url: import.meta.env.VITE_MAP_TILE_URL || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: import.meta.env.VITE_MAP_TILE_ATTRIBUTION
      || '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
  },
  terrain: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
  },
};

/**
 * Static table of state CENTROIDS only (the real eSAKSHI extracts carry no
 * work coordinates). All risk metrics are fetched live from
 * GET /api/v1/geo/risk-zones and joined onto this table by state name.
 */
const STATE_CENTROIDS = {
  'Uttar Pradesh':                       { id: 'UP', lat: 26.8467, lng: 80.9462 },
  'Maharashtra':                         { id: 'MH', lat: 19.7515, lng: 75.7139 },
  'West Bengal':                         { id: 'WB', lat: 22.9868, lng: 87.8550 },
  'Bihar':                               { id: 'BR', lat: 25.0961, lng: 85.3131 },
  'Tamil Nadu':                          { id: 'TN', lat: 11.1271, lng: 78.6569 },
  'Madhya Pradesh':                      { id: 'MP', lat: 22.9734, lng: 78.6569 },
  'Rajasthan':                           { id: 'RJ', lat: 27.0238, lng: 74.2179 },
  'Gujarat':                             { id: 'GJ', lat: 22.2587, lng: 71.1924 },
  'Karnataka':                           { id: 'KA', lat: 15.3173, lng: 75.7139 },
  'Andhra Pradesh':                      { id: 'AP', lat: 15.9129, lng: 79.7400 },
  'Odisha':                              { id: 'OR', lat: 20.9517, lng: 85.0985 },
  'Kerala':                              { id: 'KL', lat: 10.8505, lng: 76.2711 },
  'Assam':                               { id: 'AS', lat: 26.2006, lng: 92.9376 },
  'Punjab':                              { id: 'PB', lat: 31.1471, lng: 75.3412 },
  'Haryana':                             { id: 'HR', lat: 29.0588, lng: 76.0856 },
  'Jammu And Kashmir':                   { id: 'JK', lat: 33.7782, lng: 76.5762 },
  'Jharkhand':                           { id: 'JH', lat: 23.6102, lng: 85.2799 },
  'Chhattisgarh':                        { id: 'CT', lat: 21.2787, lng: 81.8661 },
  'Delhi':                               { id: 'DL', lat: 28.7041, lng: 77.1025 },
  'Telangana':                           { id: 'TS', lat: 17.8748, lng: 78.1008 },
  'Himachal Pradesh':                    { id: 'HP', lat: 31.9048, lng: 77.0934 },
  'Uttarakhand':                         { id: 'UK', lat: 30.0668, lng: 79.0193 },
  'Sikkim':                              { id: 'SK', lat: 27.5330, lng: 88.6139 },
  'Meghalaya':                           { id: 'ML', lat: 25.5460, lng: 91.3760 },
  'Mizoram':                             { id: 'MZ', lat: 23.6850, lng: 92.7350 },
  'Nagaland':                            { id: 'NG', lat: 26.1580, lng: 94.5624 },
  'Manipur':                             { id: 'MN', lat: 24.6637, lng: 93.8103 },
  'Tripura':                             { id: 'TR', lat: 23.9405, lng: 91.9882 },
  'Arunachal Pradesh':                   { id: 'AR', lat: 28.2180, lng: 94.7278 },
  'Goa':                                 { id: 'GA', lat: 15.2993, lng: 74.1240 },
  'Puducherry':                          { id: 'PY', lat: 11.9416, lng: 79.8083 },
  'Chandigarh':                          { id: 'CH', lat: 30.7333, lng: 76.7794 },
  'Ladakh':                              { id: 'LA', lat: 34.2268, lng: 77.5619 },
  'Andaman And Nicobar Islands':         { id: 'AN', lat: 11.7401, lng: 92.6586 },
  'Lakshadweep':                         { id: 'LD', lat: 10.5667, lng: 72.6427 },
  'The Dadra And Nagar Haveli And Daman And Diu': { id: 'DN', lat: 20.2667, lng: 73.0166 },
};

/** Imperative fly-to bridge: animates the map when a state is selected. */
function FlyToState({ target }) {
  const map = useMap();
  useEffect(() => {
    if (target && target.lat != null) {
      map.flyTo([target.lat, target.lng], 7, { duration: 1.2 });
    }
  }, [target, map]);
  return null;
}

export default function GeoRiskMap({ onSelectAlert }) {
  const [mapType, setMapType] = useState('street'); // 'street' | 'satellite' | 'terrain'
  const [filter, setFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState(null);
  const [flyTarget, setFlyTarget] = useState(null); // {lat,lng} to animate to
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  // Fetch real state-level risk aggregates from the backend and join them
  // onto the static centroid table (works data carries no coordinates).
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/geo/risk-zones`)
      .then(res => {
        if (!res.ok) throw new Error(`geo/risk-zones returned ${res.status}`);
        return res.json();
      })
      .then(data => {
        const merged = (data.zones || [])
          .map(z => {
            const c = STATE_CENTROIDS[z.state];
            return c ? { ...z, ...c, name: z.state } : null;
          })
          .filter(Boolean);
        setZones(merged);
        setSelectedState(merged[0] || null);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load geo risk zones', err);
        setLoadError(err.message);
        setLoading(false);
      });
  }, []);

  // Filtered zones (search + risk-status chips)
  const filteredZones = useMemo(() => {
    return zones.filter(z => {
      if (filter !== 'ALL' && z.status !== filter) return false;
      if (searchTerm && !z.name.toLowerCase().includes(searchTerm.toLowerCase().trim())) return false;
      return true;
    });
  }, [zones, filter, searchTerm]);

  // Selecting a state from the map just updates the profile card;
  // the dedicated Navigate button animates the map to it.
  const handleSelectState = (z) => setSelectedState(z);
  const handleFlyToState = (st) => {
    setSelectedState(st);
    setFlyTarget({ lat: st.lat, lng: st.lng, ts: Date.now() });
  };

  return (
    <div style={{ width: '100%' }}>
      {/* Top Sticky Header & Controls */}
      <div className="sticky-section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.5px' }}>
            Geographic Risk Map
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.85rem' }}>
            Real-time geospatial intelligence & multi-signal anomaly clustering across India.
          </p>
        </div>

        {/* Controls Toolbar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          {/* Search Box */}
          <div style={{ position: 'relative', width: '200px' }}>
            <Search size={14} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            <input
              type="text"
              placeholder="Search state..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.4rem 0.75rem 0.4rem 2.2rem',
                fontSize: '0.825rem',
                background: '#f1f5f9',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                outline: 'none'
              }}
            />
          </div>

          {/* Risk Filter Buttons */}
          <div style={{ display: 'flex', gap: '0.25rem', background: '#f1f5f9', padding: '0.2rem', borderRadius: '8px' }}>
            {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(lvl => (
              <button
                key={lvl}
                onClick={() => setFilter(lvl)}
                style={{
                  padding: '0.35rem 0.65rem',
                  borderRadius: '6px',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: filter === lvl ? '#0f172a' : 'transparent',
                  color: filter === lvl ? '#ffffff' : '#64748b',
                  transition: 'all 0.15s ease'
                }}
              >
                {lvl}
              </button>
            ))}
          </div>

          {/* Tile Layer Switcher */}
          <div style={{ display: 'flex', gap: '0.25rem', background: '#f1f5f9', padding: '0.2rem', borderRadius: '8px' }}>
            <button
              onClick={() => setMapType('street')}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                background: mapType === 'street' ? '#2563eb' : 'transparent',
                color: mapType === 'street' ? '#ffffff' : '#64748b'
              }}
            >
              Street
            </button>
            <button
              onClick={() => setMapType('satellite')}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                background: mapType === 'satellite' ? '#2563eb' : 'transparent',
                color: mapType === 'satellite' ? '#ffffff' : '#64748b'
              }}
            >
              Satellite
            </button>
            <button
              onClick={() => setMapType('terrain')}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                background: mapType === 'terrain' ? '#2563eb' : 'transparent',
                color: mapType === 'terrain' ? '#ffffff' : '#64748b'
              }}
            >
              OSM
            </button>
          </div>
        </div>
      </div>

      {/* Main Map & Live Dossier Split */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', alignItems: 'start', marginTop: '1.25rem' }}>
        
        {/* Real Leaflet Map (react-leaflet, npm-bundled) */}
        <div className="metric-card" style={{ padding: '0.75rem', background: '#ffffff', overflow: 'hidden' }}>
          <div
            style={{
              width: '100%',
              height: '560px',
              borderRadius: '8px',
              background: '#e5e7eb',
              position: 'relative',
              zIndex: 1
            }}
          >
            <MapContainer
              center={[22.8, 80.0]}
              zoom={5}
              minZoom={4}
              maxZoom={14}
              zoomControl={true}
              style={{ width: '100%', height: '100%', borderRadius: '8px' }}
            >
              <TileLayer
                key={mapType}
                url={TILE_LAYERS[mapType].url}
                attribution={TILE_LAYERS[mapType].attribution}
                maxZoom={18}
              />
              <FlyToState target={flyTarget} />
              <MarkerClusterGroup
                chunkedLoading
                maxClusterRadius={50}
                spiderfyOnMaxZoom
                showCoverageOnHover={false}
                zoomToBoundsOnClick
              >
                {filteredZones.map(z => {
                  const color = z.status === 'HIGH' ? '#ef4444' : z.status === 'MEDIUM' ? '#f59e0b' : '#10b981';
                  const isHigh = z.status === 'HIGH';

                  // Custom animated HTML Marker Icon
                  const customIcon = L.divIcon({
                    className: 'custom-leaflet-marker',
                    html: `
                      <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 34px; height: 34px;">
                        ${isHigh ? `<div style="position: absolute; width: 32px; height: 32px; border-radius: 50%; background: ${color}; opacity: 0.35; animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>` : ''}
                        <div style="background: ${color}; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 3px 10px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 9px; font-weight: 800;">
                          ${z.id}
                        </div>
                      </div>
                    `,
                    iconSize: [34, 34],
                    iconAnchor: [17, 17]
                  });

                  return (
                    <Marker
                      key={z.state}
                      position={[z.lat, z.lng]}
                      icon={customIcon}
                      eventHandlers={{ click: () => handleSelectState(z) }}
                    >
                      <Popup>
                        {/* Interactive Popup Content (real eSAKSHI aggregates) */}
                        <div style={{ padding: '4px', minWidth: 220 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', gap: '8px' }}>
                            <strong style={{ fontSize: '14px', color: '#0f172a' }}>{z.name}</strong>
                            <span style={{ background: `${color}20`, color: color, fontSize: '10px', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', border: `1px solid ${color}40` }}>
                              {z.status} RISK
                            </span>
                          </div>
                          <div style={{ fontSize: '12px', color: '#475569', lineHeight: 1.6 }}>
                            <div>• Monitored Works: <strong>{z.total_works.toLocaleString('en-IN')}</strong></div>
                            <div>• Disbursed: <strong>₹{z.disbursed_cr.toLocaleString('en-IN')} Cr</strong></div>
                            <div>• High-Risk Flags: <strong style={{ color: '#ef4444' }}>{z.high_risk_works.toLocaleString('en-IN')}</strong></div>
                            <div>• Avg Risk Score: <strong>{z.avg_risk_score}/100</strong></div>
                            <div>• Districts: <strong>{z.districts_count}</strong></div>
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MarkerClusterGroup>
            </MapContainer>
          </div>
        </div>

        {/* Right: State Profile Card */}
        <div className="metric-card" style={{ padding: '1.5rem', position: 'sticky', top: '80px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: '2rem' }}>
              Loading real state risk aggregates from the eSAKSHI database...
            </div>
          ) : loadError ? (
            <div style={{ textAlign: 'center', color: '#ef4444', padding: '2rem', fontSize: '0.85rem' }}>
              Failed to load risk zones: {loadError}
              <div style={{ color: '#94a3b8', marginTop: '0.5rem', fontSize: '0.78rem' }}>
                Ensure the API server is running.
              </div>
            </div>
          ) : selectedState ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>
                    {selectedState.name}
                  </h3>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    State Nodal Zone Profile — real eSAKSHI aggregates
                  </div>
                </div>

                <span className={`score-pill ${selectedState.status === 'HIGH' ? 'score-pill-red' : 'score-pill-green'}`}>
                  {selectedState.status} RISK
                </span>
              </div>

              {/* Stats Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Monitored Works</div>
                  <strong style={{ fontSize: '1.15rem', color: '#0f172a' }}>{selectedState.total_works.toLocaleString('en-IN')}</strong>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>High Risk Flags</div>
                  <strong style={{ fontSize: '1.15rem', color: '#ef4444' }}>{selectedState.high_risk_works.toLocaleString('en-IN')}</strong>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Disbursed Total</div>
                  <strong style={{ fontSize: '1.15rem', color: '#0f172a' }}>₹{selectedState.disbursed_cr.toLocaleString('en-IN')} Cr</strong>
                </div>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Avg Composite Score</div>
                  <strong style={{ fontSize: '1.15rem', color: selectedState.status === 'HIGH' ? '#ef4444' : '#10b981' }}>
                    {selectedState.avg_risk_score}/100
                  </strong>
                </div>
              </div>

              {/* Real multi-signal insight computed from the loaded aggregates */}
              <div style={{ background: '#f0f6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.85rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#0369a1', fontWeight: 700, fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                  <Sparkles size={14} />
                  <span>Multi-Signal Zone Finding</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#1e3a5f', lineHeight: 1.5 }}>
                  {(() => {
                    const pct = selectedState.total_works
                      ? (selectedState.high_risk_works / selectedState.total_works) * 100
                      : 0;
                    return `${selectedState.high_risk_works.toLocaleString('en-IN')} of ${selectedState.total_works.toLocaleString('en-IN')} works (${pct.toFixed(1)}%) are flagged High/Critical across ${selectedState.districts_count} districts. Average composite risk score is ${selectedState.avg_risk_score}/100 — ${selectedState.status === 'HIGH' ? 'state-level field verification is recommended.' : 'within enhanced-monitoring range.'}`;
                  })()}
                </p>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  className="btn-primary-dark"
                  style={{ flex: 1, justifyContent: 'center' }}
                  onClick={() => {
                    // Drill into the state's highest-risk work dossier
                    // (openInvestigation expects a work_id, not a state name)
                    fetch(`${API_BASE_URL}/api/v1/works?state=${encodeURIComponent(selectedState.state || selectedState.name)}&limit=1`)
                      .then(res => res.json())
                      .then(data => {
                        const top = data.works && data.works[0];
                        if (top && onSelectAlert) onSelectAlert(top.work_id);
                      })
                      .catch(err => console.error('State work lookup failed', err));
                  }}
                >
                  Inspect State Works
                </button>
                <button
                  className="btn-secondary-outline"
                  onClick={() => handleFlyToState(selectedState)}
                  title="Center map on state"
                >
                  <Navigation size={16} />
                </button>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: '2rem' }}>
              Click any state marker on the map to inspect risk details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
