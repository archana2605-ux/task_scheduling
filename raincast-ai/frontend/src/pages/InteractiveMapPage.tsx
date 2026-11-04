import React, { useState } from 'react';
import { Map, Layers, ZoomIn } from 'lucide-react';
import { RainfallMap } from '../components/map/RainfallMap';
import { LocationSearch } from '../components/forecast/LocationSearch';
import { useIndiaRegions, useHealth, useLatestCycle } from '../api/hooks';
import { Alert } from '../components/common';
import type { ForecastModel, LocationResult } from '../types';

interface InteractiveMapPageProps {
  model: ForecastModel;
}

const InteractiveMapPage: React.FC<InteractiveMapPageProps> = ({ model }) => {
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
  const [stepHours, setStepHours] = useState(24);
  const [mapClickedLoc, setMapClickedLoc] = useState<{ lat: number; lon: number } | null>(null);

  const { data: regionsData } = useIndiaRegions();
  const { data: health } = useHealth();
  const { data: cycleInfo } = useLatestCycle(model);

  const dataAvailable = health?.ecmwf_accessible ?? false;

  const handleLocationClick = (lat: number, lon: number) => {
    setMapClickedLoc({ lat, lon });
  };

  const displayLocation = selectedLocation
    ? { lat: selectedLocation.lat, lon: selectedLocation.lon, name: selectedLocation.name }
    : mapClickedLoc
    ? { ...mapClickedLoc, name: 'Clicked location' }
    : undefined;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Map size={22} className="text-sky-400" />
          Interactive Rainfall Map
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          India-focused forecast visualization — click to inspect rainfall at any location
        </p>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="metric-label mb-2 block">Search Location</label>
            <LocationSearch
              onSelect={setSelectedLocation}
              selectedLocation={selectedLocation}
            />
          </div>
          <div>
            <label className="metric-label mb-2 block">Forecast Step</label>
            <select
              value={stepHours}
              onChange={(e) => setStepHours(Number(e.target.value))}
              className="w-full bg-navy-800 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white
                         focus:outline-none focus:border-sky-500"
            >
              {[6, 12, 24, 48, 72, 120].map((h) => (
                <option key={h} value={h}>+{h}h forecast</option>
              ))}
            </select>
          </div>
          <div>
            <label className="metric-label mb-2 block">Model Init</label>
            <div className="bg-navy-800 border border-navy-700 rounded-lg px-3 py-2.5 text-sm">
              <span className="text-white font-mono">
                {cycleInfo?.init_datetime ?? '—'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ECMWF data notice */}
      {!dataAvailable && (
        <Alert
          type="info"
          title="Map Regions — Outline Mode"
          message="ECMWF forecast data is not currently accessible. The map displays India's meteorological regions as reference outlines. Connect to the internet and click 'Fetch Latest' on the Overview page to load actual rainfall data."
        />
      )}

      {/* Map */}
      <div style={{ height: '600px' }}>
        <RainfallMap
          regions={regionsData?.regions}
          selectedLocation={displayLocation}
          onLocationClick={handleLocationClick}
          dataAvailable={dataAvailable}
          stepHours={stepHours}
        />
      </div>

      {/* Clicked location info */}
      {mapClickedLoc && (
        <div className="card">
          <h3 className="section-title mb-2">Clicked Location</h3>
          <p className="text-sm text-slate-300 font-mono">
            {mapClickedLoc.lat.toFixed(4)}°N, {mapClickedLoc.lon.toFixed(4)}°E
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Navigate to Location Forecast to get the full rainfall forecast for this coordinate.
          </p>
        </div>
      )}

      {/* Map usage guide */}
      <div className="card text-sm">
        <h3 className="section-title mb-3 flex items-center gap-2">
          <ZoomIn size={16} className="text-sky-400" />
          Map Guide
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-400">
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>Click anywhere on the map to record coordinates for point forecast</span>
          </div>
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>Coloured circles show India's major meteorological sub-regions</span>
          </div>
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>IMD rainfall categories are display thresholds, not official warnings</span>
          </div>
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>Actual rainfall heatmaps require downloaded GRIB2 data</span>
          </div>
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>Use Overview page → Fetch Latest to download current ECMWF data</span>
          </div>
          <div className="flex gap-2">
            <span className="text-sky-400">•</span>
            <span>Map tiles from OpenStreetMap — base layer opacity reduced for readability</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveMapPage;
