import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap, Circle, Popup, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { IndiaRegion } from '../../types';
import { LoadingSpinner, DataUnavailableNotice } from '../common';

// Fix Leaflet default icon in Vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// India centre
const INDIA_CENTER: [number, number] = [20.5937, 78.9629];
const INDIA_ZOOM = 5;

// IMD rainfall thresholds and colors
const RAINFALL_SCALE = [
  { min: 0, max: 0, color: 'rgba(176, 224, 255, 0)', label: 'No rain' },
  { min: 0.001, max: 2.5, color: 'rgba(186, 230, 253, 0.6)', label: 'Very light' },
  { min: 2.5, max: 15, color: 'rgba(56, 189, 248, 0.65)', label: 'Light' },
  { min: 15, max: 64.5, color: 'rgba(2, 132, 199, 0.70)', label: 'Moderate' },
  { min: 64.5, max: 115.5, color: 'rgba(30, 64, 175, 0.75)', label: 'Heavy' },
  { min: 115.5, max: 204.5, color: 'rgba(126, 34, 206, 0.80)', label: 'Very heavy' },
  { min: 204.5, max: Infinity, color: 'rgba(190, 18, 60, 0.85)', label: 'Extremely heavy' },
];

function getColor(mm: number): string {
  for (const range of RAINFALL_SCALE) {
    if (mm <= range.max) return range.color;
  }
  return RAINFALL_SCALE[RAINFALL_SCALE.length - 1].color;
}

// ─── Map Click Handler ────────────────────────────────────────────────────────

interface MapClickHandlerProps {
  onLocationClick: (lat: number, lon: number) => void;
}

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onLocationClick }) => {
  const map = useMap();
  useEffect(() => {
    const handler = (e: L.LeafletMouseEvent) => {
      onLocationClick(e.latlng.lat, e.latlng.lng);
    };
    map.on('click', handler);
    return () => { map.off('click', handler); };
  }, [map, onLocationClick]);
  return null;
};

// ─── Legend ───────────────────────────────────────────────────────────────────

const MapLegend: React.FC = () => (
  <div className="absolute bottom-8 right-4 z-[1000] bg-navy-900/90 backdrop-blur border border-navy-700 rounded-lg p-3 text-xs">
    <p className="font-semibold text-white mb-2">Rainfall (mm) — IMD Scale</p>
    {RAINFALL_SCALE.slice(1).map((r) => (
      <div key={r.label} className="flex items-center gap-2 mb-1">
        <span
          className="w-4 h-3 rounded-sm border border-white/20 inline-block"
          style={{ backgroundColor: r.color }}
        />
        <span className="text-slate-300">
          {r.label} ({r.min}–{r.max === Infinity ? '∞' : r.max})
        </span>
      </div>
    ))}
    <p className="text-slate-500 mt-2 text-[10px]">Display categories only — not official warnings</p>
  </div>
);

// ─── Main Map Component ───────────────────────────────────────────────────────

interface RainfallMapProps {
  regions?: IndiaRegion[];
  selectedLocation?: { lat: number; lon: number; name?: string };
  onLocationClick?: (lat: number, lon: number) => void;
  dataAvailable?: boolean;
  isLoading?: boolean;
  stepHours?: number;
}

export const RainfallMap: React.FC<RainfallMapProps> = ({
  regions,
  selectedLocation,
  onLocationClick,
  dataAvailable = true,
  isLoading = false,
  stepHours,
}) => {
  return (
    <div className="relative w-full h-full min-h-[500px] rounded-xl overflow-hidden border border-navy-700">
      {isLoading && (
        <div className="absolute inset-0 z-[2000] bg-navy-950/80 flex items-center justify-center">
          <LoadingSpinner size="lg" label="Loading forecast data..." />
        </div>
      )}

      {!dataAvailable && !isLoading && (
        <div className="absolute top-4 left-4 right-4 z-[1000]">
          <DataUnavailableNotice />
        </div>
      )}

      <MapContainer
        center={INDIA_CENTER}
        zoom={INDIA_ZOOM}
        style={{ width: '100%', height: '100%', minHeight: '500px' }}
        className="bg-navy-950"
      >
        {/* OpenStreetMap tile layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          opacity={0.4}
        />

        {/* Click handler */}
        {onLocationClick && <MapClickHandler onLocationClick={onLocationClick} />}

        {/* Region overlays — colored by intensity when data available */}
        {regions?.map((region) => {
          const center: [number, number] = [
            (region.bbox.lat_min + region.bbox.lat_max) / 2,
            (region.bbox.lon_min + region.bbox.lon_max) / 2,
          ];
          const radiusKm =
            Math.min(
              (region.bbox.lat_max - region.bbox.lat_min) * 55,
              (region.bbox.lon_max - region.bbox.lon_min) * 55
            ) * 0.4;

          return (
            <Circle
              key={region.name}
              center={center}
              radius={radiusKm * 1000}
              pathOptions={{
                color: region.color,
                fillColor: region.color,
                fillOpacity: dataAvailable ? 0.15 : 0.08,
                weight: 1,
                opacity: 0.5,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-bold text-navy-900">{region.name}</p>
                  <p className="text-slate-600">{region.states.join(', ')}</p>
                  {!dataAvailable && (
                    <p className="text-amber-600 mt-1">Forecast data pending</p>
                  )}
                </div>
              </Popup>
            </Circle>
          );
        })}

        {/* Selected location marker */}
        {selectedLocation && (
          <Marker position={[selectedLocation.lat, selectedLocation.lon]}>
            <Popup>
              <div className="text-xs">
                <p className="font-bold">{selectedLocation.name || 'Selected Location'}</p>
                <p className="text-slate-600">
                  {selectedLocation.lat.toFixed(4)}°N, {selectedLocation.lon.toFixed(4)}°E
                </p>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      <MapLegend />

      {/* Step indicator */}
      {stepHours !== undefined && (
        <div className="absolute top-4 left-4 z-[1000] bg-navy-900/90 backdrop-blur border border-navy-700 rounded-lg px-3 py-1.5">
          <p className="text-xs text-slate-400">Forecast lead time</p>
          <p className="text-sm font-bold text-sky-300">+{stepHours}h</p>
        </div>
      )}
    </div>
  );
};
