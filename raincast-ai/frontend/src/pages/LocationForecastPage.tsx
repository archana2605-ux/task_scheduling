import React, { useState } from 'react';
import { MapPin, Download, TrendingUp } from 'lucide-react';
import { LocationSearch } from '../components/forecast/LocationSearch';
import { useLocationForecast } from '../api/hooks';
import {
  HourlyRainfallChart,
  AccumulatedRainfallChart,
  PeriodSummaryChart,
  RainfallDistributionChart,
} from '../components/dashboard/Charts';
import { LoadingSpinner, Alert, RainfallIntensityBadge, DataUnavailableNotice } from '../components/common';
import { getLocationForecastCsvUrl } from '../api/client';
import { classifyRainfall } from '../types';
import type { ForecastModel, LocationResult } from '../types';

interface LocationForecastPageProps {
  model: ForecastModel;
}

const LocationForecastPage: React.FC<LocationForecastPageProps> = ({ model }) => {
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
  const [maxStep, setMaxStep] = useState(72);

  const lat = selectedLocation?.lat ?? null;
  const lon = selectedLocation?.lon ?? null;

  const { data, isLoading, error } = useLocationForecast(lat, lon, model, maxStep);

  const csvUrl = selectedLocation
    ? getLocationForecastCsvUrl(lat!, lon!, model, selectedLocation.name)
    : null;

  const forecast = data?.forecast;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Location Forecast</h1>
          <p className="text-sm text-slate-400 mt-1">
            Point rainfall forecast for any India location
          </p>
        </div>
        {csvUrl && (
          <a
            href={csvUrl}
            download
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Download size={14} />
            Export CSV
          </a>
        )}
      </div>

      {/* Location Search + Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="metric-label mb-2 block">Search Location</label>
            <LocationSearch
              onSelect={setSelectedLocation}
              selectedLocation={selectedLocation}
            />
          </div>
          <div>
            <label className="metric-label mb-2 block">Forecast Horizon</label>
            <select
              value={maxStep}
              onChange={(e) => setMaxStep(Number(e.target.value))}
              className="w-full bg-navy-800 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white
                         focus:outline-none focus:border-sky-500"
            >
              <option value={24}>+24 hours</option>
              <option value={48}>+48 hours</option>
              <option value={72}>+72 hours</option>
              <option value={120}>+120 hours</option>
              <option value={240}>+240 hours</option>
            </select>
          </div>
        </div>
      </div>

      {/* No location selected */}
      {!selectedLocation && (
        <div className="card flex flex-col items-center py-12 gap-3">
          <MapPin size={40} className="text-slate-600" />
          <p className="text-slate-400 font-medium">Select a location to view its forecast</p>
          <p className="text-sm text-slate-500">
            Search for a city, district, or state above
          </p>
        </div>
      )}

      {/* Loading */}
      {selectedLocation && isLoading && (
        <div className="card flex justify-center py-12">
          <LoadingSpinner label="Fetching ECMWF forecast data..." />
        </div>
      )}

      {/* Error */}
      {selectedLocation && error && !isLoading && (
        <DataUnavailableNotice model={model} />
      )}

      {/* Forecast data */}
      {forecast && !isLoading && (
        <>
          {/* Location summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              {
                label: 'Next 24h',
                value: forecast.total_24h_mm.toFixed(1),
                unit: 'mm',
                color: 'text-sky-300',
              },
              {
                label: 'Next 48h',
                value: forecast.total_48h_mm.toFixed(1),
                unit: 'mm',
                color: 'text-blue-300',
              },
              {
                label: 'Next 72h',
                value: forecast.total_72h_mm.toFixed(1),
                unit: 'mm',
                color: 'text-indigo-300',
              },
              {
                label: 'Peak Intensity',
                value: forecast.max_step_mm.toFixed(1),
                unit: 'mm/step',
                color: 'text-amber-300',
              },
            ].map((m) => (
              <div key={m.label} className="metric-card">
                <p className="metric-label">{m.label}</p>
                <p className={`metric-value ${m.color}`}>
                  {m.value}
                  <span className="metric-unit ml-1">{m.unit}</span>
                </p>
              </div>
            ))}
          </div>

          {/* Model & location metadata */}
          <div className="card text-sm">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="metric-label">Location</p>
                <p className="text-white font-medium">{selectedLocation?.name}</p>
                <p className="text-slate-400 text-xs">{selectedLocation?.state}</p>
              </div>
              <div>
                <p className="metric-label">Coordinates</p>
                <p className="text-white font-mono text-xs">
                  {lat?.toFixed(4)}°N, {lon?.toFixed(4)}°E
                </p>
              </div>
              <div>
                <p className="metric-label">Model Init</p>
                <p className="text-white font-mono text-xs">{forecast.metadata.init_datetime}</p>
              </div>
              <div>
                <p className="metric-label">Peak Rainfall Class</p>
                <RainfallIntensityBadge intensity={classifyRainfall(forecast.max_step_mm)} />
              </div>
            </div>
          </div>

          {/* Charts */}
          <HourlyRainfallChart steps={forecast.steps} title={`Rainfall Forecast — ${selectedLocation?.name}`} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AccumulatedRainfallChart steps={forecast.steps} />
            <PeriodSummaryChart forecast={forecast} />
          </div>

          <RainfallDistributionChart steps={forecast.steps} />

          {/* Step table */}
          <div className="card overflow-hidden">
            <h3 className="section-title mb-4">Forecast Step Detail</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-navy-700">
                    {['Lead Time', 'Incremental (mm)', 'Accumulated (mm)', 'Period (h)', 'Intensity'].map((h) => (
                      <th key={h} className="text-left py-2 px-3 text-slate-400 text-xs font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {forecast.steps.map((step, i) => (
                    <tr
                      key={step.step_hours}
                      className={`border-b border-navy-800 ${i % 2 === 0 ? 'bg-navy-900/30' : ''}`}
                    >
                      <td className="py-2 px-3 text-sky-300 font-mono font-medium">
                        +{step.step_hours}h
                      </td>
                      <td className="py-2 px-3 text-white font-mono">
                        {step.incremental_mm.toFixed(2)}
                      </td>
                      <td className="py-2 px-3 text-slate-300 font-mono">
                        {step.accumulated_mm.toFixed(2)}
                      </td>
                      <td className="py-2 px-3 text-slate-400">
                        {step.accumulation_period_h}h
                      </td>
                      <td className="py-2 px-3">
                        <RainfallIntensityBadge intensity={classifyRainfall(step.incremental_mm)} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LocationForecastPage;
