import React, { useState } from 'react';
import { CloudRain, Download, RefreshCw } from 'lucide-react';
import { useLatestCycle, useAvailableSteps, useDownloadForecast, useForecastSummary } from '../api/hooks';
import {
  HourlyRainfallChart,
  AccumulatedRainfallChart,
  PeriodSummaryChart,
  RainfallDistributionChart,
} from '../components/dashboard/Charts';
import { LoadingSpinner, Alert, DataUnavailableNotice, MetricCard } from '../components/common';
import type { ForecastModel } from '../types';

interface LiveForecastPageProps {
  model: ForecastModel;
}

const LiveForecastPage: React.FC<LiveForecastPageProps> = ({ model }) => {
  const [maxStep, setMaxStep] = useState(72);
  const { data: cycleInfo } = useLatestCycle(model);
  const { data: summary } = useForecastSummary(model);
  const { data: stepsData } = useAvailableSteps(model, cycleInfo?.latest_cycle ?? 0, maxStep);
  const downloadMutation = useDownloadForecast();

  const handleFetch = () => {
    downloadMutation.mutate({ model, maxStep });
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <CloudRain size={22} className="text-sky-400" />
            Live Forecast — {model.toUpperCase()}
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Latest ECMWF {model.toUpperCase()} operational forecast
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={maxStep}
            onChange={(e) => setMaxStep(Number(e.target.value))}
            className="bg-navy-800 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
          >
            {[24, 48, 72, 120, 240].map((h) => <option key={h} value={h}>+{h}h</option>)}
          </select>
          <button onClick={handleFetch} disabled={downloadMutation.isPending} className="btn-primary flex items-center gap-2">
            {downloadMutation.isPending ? <RefreshCw size={14} className="animate-spin" /> : <Download size={14} />}
            {downloadMutation.isPending ? 'Fetching...' : 'Fetch Data'}
          </button>
        </div>
      </div>

      {/* Status feedback */}
      {downloadMutation.isSuccess && (
        <Alert type="success" title="Data fetched" message={`${model.toUpperCase()} forecast data downloaded successfully. Processing complete.`} />
      )}
      {downloadMutation.isError && (
        <Alert type="error" title="Fetch failed"
          message={`Could not retrieve ${model.toUpperCase()} forecast: ${(downloadMutation.error as Error)?.message}. ECMWF data requires internet connectivity to data.ecmwf.int.`} />
      )}

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Model" value={model.toUpperCase()} color="text-sky-300" />
        <MetricCard
          label="Init Date"
          value={cycleInfo?.latest_date ?? '—'}
          color="text-slate-200"
        />
        <MetricCard
          label="Init Cycle"
          value={cycleInfo ? `${String(cycleInfo.latest_cycle).padStart(2, '0')}:00 UTC` : '—'}
          color="text-slate-200"
        />
        <MetricCard
          label="Available Steps"
          value={stepsData?.count ?? '—'}
          unit="steps"
          color="text-emerald-300"
        />
      </div>

      {/* Available steps info */}
      {stepsData && (
        <div className="card">
          <h3 className="section-title mb-3">Available Forecast Steps</h3>
          <div className="flex flex-wrap gap-2">
            {stepsData.steps.map((step: number) => (
              <span key={step} className="font-mono text-xs bg-navy-800 border border-navy-700 rounded px-2 py-1 text-sky-300">
                +{step}h
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Steps up to +{maxStep}h for {model.toUpperCase()} cycle {String(cycleInfo?.latest_cycle ?? 0).padStart(2, '0')}Z
          </p>
        </div>
      )}

      {/* Data not yet downloaded */}
      {!downloadMutation.isSuccess && !downloadMutation.isPending && (
        <div className="card flex flex-col items-center py-12 gap-4">
          <CloudRain size={40} className="text-slate-600" />
          <p className="text-slate-400 font-medium">No forecast data loaded yet</p>
          <p className="text-sm text-slate-500 max-w-md text-center">
            Click <strong className="text-white">Fetch Data</strong> to download the latest ECMWF{' '}
            {model.toUpperCase()} forecast from data.ecmwf.int. This requires internet connectivity
            and downloads a GRIB2 file (~50–200 MB).
          </p>
          <button onClick={handleFetch} className="btn-primary flex items-center gap-2 mt-2">
            <Download size={14} />
            Fetch Latest {model.toUpperCase()} Forecast
          </button>
        </div>
      )}

      {downloadMutation.isPending && (
        <div className="card flex justify-center py-16">
          <LoadingSpinner size="lg" label={`Downloading ECMWF ${model.toUpperCase()} GRIB2 file...`} />
        </div>
      )}
    </div>
  );
};

export default LiveForecastPage;
