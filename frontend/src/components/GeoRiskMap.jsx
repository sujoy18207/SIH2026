import React, { useState, useEffect, useRef } from 'react';
import { MapPin, ShieldAlert, Layers, Search, ArrowUpRight, Globe, Navigation } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

export default function GeoRiskMap({ onSelectAlert }) {
  const mapRef = useRef(null);
  const gmapInstance = useRef(null);
  const markersRef = useRef([]);
  const circlesRef = useRef([]);
  const infoWindowRef = useRef(null);

  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [zoneFilter, setZoneFilter] = useState('ALL'); // 'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'
  const [selectedZone, setSelectedZone] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [mapType, setMapType] = useState('roadmap'); // 'roadmap' | 'satellite' | 'terrain' | 'hybrid'

  // Fetch geographic risk zones from backend
  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE_URL}/api/v1/geo/risk-zones`)
      .then(res => res.json())
      .then(data => {
        setZones(data.zones || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load geo risk zones", err);
        setLoading(false);
      });
  }, []);

  // Initialize Google Maps
  useEffect(() => {
    if (!mapRef.current) return;

    const checkGoogleMaps = () => {
      if (window.google && window.google.maps) {
        if (!gmapInstance.current) {
          const map = new window.google.maps.Map(mapRef.current, {
            center: { lat: 22.8, lng: 80.0 },
            zoom: 5,
            minZoom: 4,
            maxZoom: 12,
            mapTypeId: mapType,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: true,
            zoomControl: true,
            styles: [
              { featureType: "water", elementType: "geometry", stylers: [{ color: "#e9edf2" }] },
              { featureType: "landscape", elementType: "geometry", stylers: [{ color: "#f8fafc" }] },
              { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
              { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] }
            ]
          });

          infoWindowRef.current = new window.google.maps.InfoWindow();
          gmapInstance.current = map;
        }
      } else {
        setTimeout(checkGoogleMaps, 300);
      }
    };

    checkGoogleMaps();
  }, []);

  // Update map type
  useEffect(() => {
    if (gmapInstance.current) {
      gmapInstance.current.setMapTypeId(mapType);
    }
  }, [mapType]);

  // Render Google Maps Pins & Glowing Circles
  useEffect(() => {
    if (!gmapInstance.current || !window.google || zones.length === 0) return;

    // Clear previous markers & circles
    markersRef.current.forEach(m => m.setMap(null));
    circlesRef.current.forEach(c => c.setMap(null));
    markersRef.current = [];
    circlesRef.current = [];

    const filtered = zones.filter(z => {
      if (zoneFilter !== 'ALL' && z.zone_type !== zoneFilter) return false;
      if (searchTerm && !z.state_name.toLowerCase().includes(searchTerm.toLowerCase().trim())) return false;
      return true;
    });

    filtered.forEach(z => {
      const pos = { lat: z.lat, lng: z.lon };
      const color = z.zone_color || (z.zone_type === 'HIGH' ? '#dc2626' : z.zone_type === 'MEDIUM' ? '#f59e0b' : '#16a34a');
      const radiusMeters = z.zone_type === 'HIGH' ? 85000 : z.zone_type === 'MEDIUM' ? 65000 : 50000;

      // 1. Glowing Zone Circle
      const circle = new window.google.maps.Circle({
        strokeColor: color,
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: color,
        fillOpacity: z.zone_type === 'HIGH' ? 0.22 : 0.15,
        map: gmapInstance.current,
        center: pos,
        radius: radiusMeters,
        clickable: true
      });
      circlesRef.current.push(circle);

      // 2. Custom SVG Pin Marker
      const pinSvg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="34" height="42" viewBox="0 0 34 42">
          <path d="M17 0C7.61 0 0 7.61 0 17C0 29.75 17 42 17 42C17 42 34 29.75 34 17C34 7.61 26.39 0 17 0Z" fill="${color}" stroke="#ffffff" stroke-width="2"/>
          <circle cx="17" cy="17" r="7" fill="#ffffff"/>
          <circle cx="17" cy="17" r="4" fill="${color}"/>
        </svg>
      `;

      const marker = new window.google.maps.Marker({
        position: pos,
        map: gmapInstance.current,
        title: `${z.state_name} (${z.zone_type} Risk)`,
        icon: {
          url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(pinSvg)}`,
          scaledSize: new window.google.maps.Size(30, 38),
          anchor: new window.google.maps.Point(15, 38)
        },
        animation: z.zone_type === 'HIGH' ? window.google.maps.Animation.DROP : null
      });
      markersRef.current.push(marker);

      // Interactive InfoWindow
      const expCr = (z.total_expenditure / 10000000).toFixed(1);
      const infoContent = `
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 6px; min-width: 230px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <strong style="font-size: 14px; color: #0f2744;">${z.state_name}</strong>
            <span style="background: ${color}20; color: ${color}; font-weight: 800; font-size: 11px; padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}40;">
              ${z.zone_type} RISK
            </span>
          </div>
          <div style="font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 6px;">
            <div>• Total Projects: <strong>${z.total_projects.toLocaleString()}</strong></div>
            <div>• Disbursed: <strong>₹${expCr} Cr</strong></div>
            <div>• High Risk Flags: <strong style="color: #dc2626;">${z.high_risk_count}</strong></div>
            <div>• Avg Risk Score: <strong>${z.avg_risk_score} / 100</strong></div>
          </div>
          ${z.top_flagged_work ? `
            <div style="border-top: 1px dashed #cbd5e1; padding-top: 6px; font-size: 11px; color: #334155;">
              <div style="color: #64748b; font-weight: 600;">Top Flagged Project:</div>
              <div style="font-weight: 700; color: #0f2744; margin-top: 2px;">#${z.top_flagged_work.work_id} (${z.top_flagged_work.mp_name || 'MP'})</div>
              <div style="color: #dc2626; font-weight: 700; margin-top: 2px;">Risk Score: ${z.top_flagged_work.risk_score} / 100</div>
            </div>
          ` : ''}
        </div>
      `;

      const clickHandler = () => {
        setSelectedZone(z);
        if (infoWindowRef.current) {
          infoWindowRef.current.setContent(infoContent);
          infoWindowRef.current.open(gmapInstance.current, marker);
        }
      };

      marker.addListener('click', clickHandler);
      circle.addListener('click', clickHandler);
    });
  }, [zones, zoneFilter, searchTerm]);

  // Fly to state
  const handleFlyToState = (z) => {
    setSelectedZone(z);
    if (gmapInstance.current) {
      gmapInstance.current.panTo({ lat: z.lat, lng: z.lon });
      gmapInstance.current.setZoom(7);
      
      const targetMarker = markersRef.current.find(m => m.getTitle().startsWith(z.state_name));
      if (targetMarker && infoWindowRef.current) {
        const expCr = (z.total_expenditure / 10000000).toFixed(1);
        const color = z.zone_color || '#dc2626';
        infoWindowRef.current.setContent(`
          <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 6px; min-width: 230px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
              <strong style="font-size: 14px; color: #0f2744;">${z.state_name}</strong>
              <span style="background: ${color}20; color: ${color}; font-weight: 800; font-size: 11px; padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}40;">
                ${z.zone_type} RISK
              </span>
            </div>
            <div style="font-size: 12px; color: #475569; line-height: 1.5;">
              <div>• Total Projects: <strong>${z.total_projects.toLocaleString()}</strong></div>
              <div>• Disbursed: <strong>₹${expCr} Cr</strong></div>
              <div>• High Risk Flags: <strong style="color: #dc2626;">${z.high_risk_count}</strong></div>
              <div>• Avg Risk Score: <strong>${z.avg_risk_score} / 100</strong></div>
            </div>
          </div>
        `);
        infoWindowRef.current.open(gmapInstance.current, targetMarker);
      }
    }
  };

  const highRiskZones = zones.filter(z => z.zone_type === 'HIGH');
  const mediumRiskZones = zones.filter(z => z.zone_type === 'MEDIUM');
  const lowRiskZones = zones.filter(z => z.zone_type === 'LOW');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header Banner & Legend */}
      <div className="goi-card">
        <div className="goi-card-header">
          <div>
            <div className="goi-card-title">
              <MapPin size={22} color="#dc2626" />
              Google Maps Pan-India Risk & Anomaly Intelligence Map
            </div>
            <div style={{ fontSize: '0.825rem', color: '#64748b', marginTop: '0.2rem' }}>
              Real-time Google Maps geospatial intelligence across all 36 States & Union Territories
            </div>
          </div>

          {/* Map Color Legend */}
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', background: '#f8fafc', padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 700, color: '#dc2626' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#dc2626', display: 'inline-block' }} />
              High Risk Zone ({highRiskZones.length})
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 700, color: '#d97706' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b', display: 'inline-block' }} />
              Medium Risk Zone ({mediumRiskZones.length})
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', fontWeight: 700, color: '#16a34a' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#16a34a', display: 'inline-block' }} />
              Low Risk Zone ({lowRiskZones.length})
            </div>
          </div>
        </div>

        {/* Filter Controls & Map Type Switcher Toolbar */}
        <div style={{ padding: '0.75rem 1.5rem', background: '#ffffff', borderTop: '1px solid var(--goi-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setZoneFilter('ALL')}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: zoneFilter === 'ALL' ? '#0f2744' : '#ffffff',
                color: zoneFilter === 'ALL' ? '#ffffff' : '#475569'
              }}
            >
              All States ({zones.length})
            </button>

            <button
              onClick={() => setZoneFilter('HIGH')}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #fecaca',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: zoneFilter === 'HIGH' ? '#dc2626' : '#fff5f5',
                color: zoneFilter === 'HIGH' ? '#ffffff' : '#dc2626'
              }}
            >
              🔴 High Risk ({highRiskZones.length})
            </button>

            <button
              onClick={() => setZoneFilter('MEDIUM')}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #fde68a',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: zoneFilter === 'MEDIUM' ? '#f59e0b' : '#fffbeb',
                color: zoneFilter === 'MEDIUM' ? '#ffffff' : '#b45309'
              }}
            >
              🟡 Medium Risk ({mediumRiskZones.length})
            </button>

            <button
              onClick={() => setZoneFilter('LOW')}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #bbf7d0',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                background: zoneFilter === 'LOW' ? '#16a34a' : '#f0fdf4',
                color: zoneFilter === 'LOW' ? '#ffffff' : '#15803d'
              }}
            >
              🟢 Low Risk ({lowRiskZones.length})
            </button>
          </div>

          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            {/* Google Map Type Switcher */}
            <div style={{ display: 'flex', background: '#f1f5f9', padding: '0.2rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}>
              <button
                onClick={() => setMapType('roadmap')}
                style={{
                  padding: '0.25rem 0.6rem',
                  borderRadius: '4px',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: mapType === 'roadmap' ? '#ffffff' : 'transparent',
                  color: mapType === 'roadmap' ? '#0f2744' : '#64748b'
                }}
              >
                Map
              </button>
              <button
                onClick={() => setMapType('satellite')}
                style={{
                  padding: '0.25rem 0.6rem',
                  borderRadius: '4px',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: mapType === 'satellite' ? '#ffffff' : 'transparent',
                  color: mapType === 'satellite' ? '#0f2744' : '#64748b'
                }}
              >
                Satellite
              </button>
              <button
                onClick={() => setMapType('terrain')}
                style={{
                  padding: '0.25rem 0.6rem',
                  borderRadius: '4px',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  background: mapType === 'terrain' ? '#ffffff' : 'transparent',
                  color: mapType === 'terrain' ? '#0f2744' : '#64748b'
                }}
              >
                Terrain
              </button>
            </div>

            <div style={{ position: 'relative', width: '220px' }}>
              <Search size={14} color="#94a3b8" style={{ position: 'absolute', left: '10px', top: '10px' }} />
              <input
                type="text"
                placeholder="Search State on Map..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="goi-input"
                style={{ paddingLeft: '2rem', padding: '0.35rem 0.75rem 0.35rem 2rem', fontSize: '0.8rem' }}
              />
            </div>
          </div>

        </div>

        {/* Google Map & Detail Split View */}
        <div style={{ display: 'grid', gridTemplateColumns: selectedZone ? '1fr 340px' : '1fr', minHeight: '520px', position: 'relative' }}>
          
          {/* Google Map Canvas */}
          <div
            ref={mapRef}
            id="google-map-container"
            style={{ width: '100%', height: '520px', background: '#e2e8f0' }}
          />

          {/* Selected Zone Side Panel */}
          {selectedZone && (
            <div style={{
              background: '#ffffff',
              borderLeft: '1px solid var(--goi-border)',
              padding: '1.25rem',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 800 }}>STATE RISK DOSSIER</div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2744', margin: '0.1rem 0' }}>
                    {selectedZone.state_name}
                  </h3>
                </div>
                <span style={{
                  padding: '0.25rem 0.6rem',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  background: `${selectedZone.zone_color}20`,
                  color: selectedZone.zone_color,
                  border: `1px solid ${selectedZone.zone_color}40`
                }}>
                  {selectedZone.zone_type} RISK
                </span>
              </div>

              {/* State Summary Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                <div style={{ background: '#f8fafc', padding: '0.6rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>TOTAL PROJECTS</div>
                  <div style={{ fontWeight: 800, color: '#0f2744', fontSize: '1rem' }}>{selectedZone.total_projects.toLocaleString()}</div>
                </div>
                <div style={{ background: '#f8fafc', padding: '0.6rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>DISBURSED (₹)</div>
                  <div style={{ fontWeight: 800, color: '#0f2744', fontSize: '1rem' }}>₹{(selectedZone.total_expenditure / 10000000).toFixed(1)} Cr</div>
                </div>
                <div style={{ background: '#fff5f5', padding: '0.6rem', borderRadius: '6px', border: '1px solid #fed7d7' }}>
                  <div style={{ fontSize: '0.7rem', color: '#c53030' }}>HIGH RISK FLAGS</div>
                  <div style={{ fontWeight: 800, color: '#c53030', fontSize: '1rem' }}>{selectedZone.high_risk_count}</div>
                </div>
                <div style={{ background: '#f8fafc', padding: '0.6rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>MAX RISK SCORE</div>
                  <div style={{ fontWeight: 800, color: '#d97706', fontSize: '1rem' }}>{selectedZone.max_risk_score} / 100</div>
                </div>
              </div>

              {/* Top Flagged Project in State */}
              {selectedZone.top_flagged_work && (
                <div style={{ background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: '6px', padding: '0.85rem' }}>
                  <div style={{ fontSize: '0.72rem', color: '#9b2c2c', fontWeight: 800, marginBottom: '0.3rem' }}>
                    HIGHEST RISK WORK IN STATE
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#0f2744' }}>
                    Project #{selectedZone.top_flagged_work.work_id}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#475569', marginTop: '0.2rem' }}>
                    "{selectedZone.top_flagged_work.description}"
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                    Hon'ble MP: <strong>{selectedZone.top_flagged_work.mp_name || 'MP'}</strong>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#dc2626', fontWeight: 700, marginTop: '0.3rem' }}>
                    Risk Score: {selectedZone.top_flagged_work.risk_score} / 100
                  </div>

                  <button
                    onClick={() => onSelectAlert && onSelectAlert(selectedZone.top_flagged_work.work_id)}
                    className="btn-goi-primary"
                    style={{ marginTop: '0.75rem', width: '100%', fontSize: '0.78rem', padding: '0.4rem' }}
                  >
                    Inspect Project Dossier
                    <ArrowUpRight size={14} />
                  </button>
                </div>
              )}

              <button
                onClick={() => setSelectedZone(null)}
                className="btn-esakshi-outline"
                style={{ fontSize: '0.78rem', padding: '0.4rem' }}
              >
                Close State Details
              </button>
            </div>
          )}

        </div>
      </div>

      {/* State Risk Matrix Grid */}
      <div className="goi-card">
        <div className="goi-card-header">
          <div className="goi-card-title">
            <Layers size={18} color="#0f2744" />
            Pan-India State Risk Matrix & Anomaly Distribution
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Click on any state row to instantly pinpoint and zoom on Google Maps
          </div>
        </div>

        <div className="goi-table-container">
          <table className="goi-table">
            <thead>
              <tr>
                <th>State / Union Territory</th>
                <th>Risk Classification Zone</th>
                <th>Total Projects</th>
                <th>Total Disbursed (₹ Cr)</th>
                <th>High Risk Works</th>
                <th>Average Risk</th>
                <th style={{ textAlign: 'right' }}>Map Action</th>
              </tr>
            </thead>
            <tbody>
              {zones.map(z => (
                <tr
                  key={z.state_name}
                  onClick={() => handleFlyToState(z)}
                  style={{ cursor: 'pointer', background: selectedZone?.state_name === z.state_name ? '#f0f9ff' : 'transparent' }}
                >
                  <td style={{ fontWeight: 700, color: '#0f2744' }}>
                    {z.state_name}
                  </td>

                  <td>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      padding: '0.2rem 0.55rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      background: `${z.zone_color}18`,
                      color: z.zone_color,
                      border: `1px solid ${z.zone_color}35`
                    }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: z.zone_color }} />
                      {z.zone_type} RISK
                    </span>
                  </td>

                  <td style={{ fontWeight: 600 }}>{z.total_projects.toLocaleString()}</td>
                  <td>₹{(z.total_expenditure / 10000000).toFixed(1)} Cr</td>
                  <td style={{ fontWeight: 700, color: z.high_risk_count > 0 ? '#dc2626' : '#16a34a' }}>
                    {z.high_risk_count}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <div className="progress-bar-container" style={{ width: '60px', height: '6px' }}>
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${Math.min(100, z.avg_risk_score * 4)}%`,
                            background: z.zone_color
                          }}
                        />
                      </div>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{z.avg_risk_score}</span>
                    </div>
                  </td>

                  <td style={{ textAlign: 'right' }}>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleFlyToState(z); }}
                      className="btn-esakshi-outline"
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                    >
                      Locate on Map 📍
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
