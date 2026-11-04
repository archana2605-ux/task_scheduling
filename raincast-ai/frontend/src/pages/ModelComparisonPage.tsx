import React, { useState } from 'react';
import { GitCompare, Info, AlertTriangle } from 'lucide-react';
import { useModelComparison, useModelInfo } from '../api/hooks';
import { ModelComparisonChart, HourlyRainfallChart } from '../components/dashboard/Charts';
import { LoadingSpinner, Alert, DataUnavailableNotice } from '../components/common';
import { LocationSearch } from '../components/forecast/LocationSearch';
import type { LocationResult } from '../types';

const ModelComparisonPage: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>({
    name: 'India Centre',
    state: '',
    district: '',
    lat: 20.5937,
    lon: 78.9629,
  });
  const [maxStep, setMaxStep] = useState(72);

  const lat = selectedLocation?.lat ?? 20.5937;
  const lon = selectedLocation?.lon ?? 78.9629;

  const { data: comparison, isLoading, error } = useModelComparison(lat, lon, maxStep);
  const { data: modelInfo } = useModelInfo();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <GitCompare size={22} className="text-sky-400" />
          IFS vs AIFS Model Comparison
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Compare ECMWF IFS (NWP) and AIFS (ML) forecasts for the same location
        </p>
      </div>

      {/* Important disclaimer */}
      <Alert
        type="info"
        title="About IFS and AIFS"
        message="IFS is ECMWF's physics-based Numerical Weather Prediction model. AIFS is ECMWF's Machine Learning model. RainCast AI retrieves operational ECMWF open data — it does not train or modify these models. Differences between models represent genuine forecast uncertainty."
      />

      {/* Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="metric-label mb-2 block">Location</label>
            <LocationSearch onSelect={setSelectedLocation} selectedLocation={selectedLocation} />
          </div>
          <div>
            <label className="metric-label mb-2 block">Forecast Horizon</label>
            <select
              value={maxStep}
              onChange={(e) => setMaxStep(Number(e.target.value))}
              className="w-full bg-navy-800 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500"
            >
              {[24, 48, 72, 120].map((h) => (
                <option key={h} value={h}>+{h} hours</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="card flex justify-center py-12">
          <LoadingSpinner label="Fetching IFS and AIFS forecasts..." />
        </div>
      )}

      {error && !isLoading && <DataUnavailableNotice />}

      {comparison && !isLoading && (
        <>
          {/* Comparison notes */}
          {comparison.notes.length > 0 && (
            <div className="card space-y-2">
              {comparison.notes.map((note, i) => (
                <p key={i} className={`text-xs flex gap-2 ${note.includes('WARNING') ? 'text-amber-400' : 'text-slate-400'}`}>
                  <span>{note.includes('WARNING') ? '⚠' : 'ℹ'}</span>
                  <span>{note}</span>
                </p>
              ))}
            </div>
          )}

          {/* Summary metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'IFS 24h Total', value: comparison.ifs?.total_24h_mm.toFixed(1) ?? '—', unit: 'mm', color: 'text-sky-300' },
              { label: 'AIFS 24h Total', value: comparison.aifs?.total_24h_mm.toFixed(1) ?? '—', unit: 'mm', color: 'text-purple-300' },
              { label: 'Max Difference', value: comparison.max_diff_mm?.toFixed(2) ?? '—', unit: 'mm', color: 'text-amber-300' },
              { label: 'Mean Difference', value: comparison.mean_diff_mm?.toFixed(2) ?? '—', unit: 'mm', color: 'text-emerald-300' },
            ].map((m) => (
              <div key={m.label} className="metric-card">
                <p className="metric-label">{m.label}</p>
                <p className={`metric-value ${m.color}`}>
                  {m.value}
                  {m.unit && <span className="metric-unit ml-1">{m.unit}</span>}
                </p>
              </div>
            ))}
          </div>

          {/* Comparison chart */}
          <ModelComparisonChart
            ifsSteps={comparison.ifs?.steps}
            aifsSteps={comparison.aifs?.steps}
          />

          {/* Side-by-side hourly */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {comparison.ifs && (
              <HourlyRainfallChart steps={comparison.ifs.steps} title="IFS — Hourly Rainfall" />
            )}
            {comparison.aifs && (
              <HourlyRainfallChart steps={comparison.aifs.steps} title="AIFS — Hourly Rainfall" />
            )}
          </div>

          {/* Comparison table */}
          {comparison.ifs && comparison.aifs && comparison.comparison_valid && (
            <div className="card overflow-hidden">
              <h3 className="section-title mb-4">Step-by-Step Comparison (mm incremental)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-navy-700">
                      {['Lead Time', 'IFS (mm)', 'AIFS (mm)', 'Difference (mm)'].map((h) => (
                        <th key={h} className="text-left py-2 px-3 text-slate-400 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(() => {
                      const ifsMap = new Map(comparison.ifs!.steps.map((s) => [s.step_hours, s.incremental_mm]));
                      const aifsMap = new Map(comparison.aifs!.steps.map((s) => [s.step_hours, s.incremental_mm]));
                      const steps = [...new Set([...ifsMap.keys(), ...aifsMap.keys()])].sort((a, b) => a - b);
                      return steps.map((step, i) => {
                        const ifs = ifsMap.get(step);
                        const aifs = aifsMap.get(step);
                        const diff = ifs !== undefined && aifs !== undefined ? ifs - aifs : null;
                        return (
                          <tr key={step} className={`border-b border-navy-800 ${i % 2 === 0 ? 'bg-navy-900/30' : ''}`}>
                            <td className="py-2 px-3 text-sky-300 font-mono font-medium">+{step}h</td>
                            <td className="py-2 px-3 text-blue-300 font-mono">{ifs?.toFixed(2) ?? '—'}</td>
                            <td className="py-2 px-3 text-purple-300 font-mono">{aifs?.toFixed(2) ?? '—'}</td>
                            <td className={`py-2 px-3 font-mono ${diff === null ? 'text-slate-500' : diff > 0 ? 'text-sky-400' : diff < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                              {diff !== null ? (diff >= 0 ? '+' : '') + diff.toFixed(2) : '—'}
                            </td>
                          </tr>
                        );
                      });
                    })()}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Model info cards */}
      {modelInfo && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(modelInfo.models).map(([name, info]: [string, any]) => (
            <div key={name} className="card border-l-4 border-sky-600">
              <h3 className="section-title mb-3 flex items-center gap-2">
                <Info size={16} className="text-sky-400" />
                {info.full_name}
              </h3>
              <div className="space-y-2 text-sm">
                {[
                  ['Type', info.type],
                  ['Developer', info.developer],
                  ['Resolution', info.resolution],
                  ['Max Lead Time', `${info.max_lead_time_hours}h`],
                  ['Cycles', info.cycles.map((c: number) => `${c.toString().padStart(2, '0')}Z`).join(', ')],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between py-1 border-b border-navy-700">
                    <span className="text-slate-400">{label}</span>
                    <span className="text-white">{value}</span>
                  </div>
                ))}
                <p className="text-xs text-slate-400 mt-2 italic">{info.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelComparisonPage;
