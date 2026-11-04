import React from 'react';
import { CloudRain, Activity, TrendingUp, Layers, AlertCircle, Download, RefreshCw } from 'lucide-react';
import { useForecastSummary, useLatestCycle, useHealth, useDownloadForecast, useCachedForecasts } from '../api/hooks';
import { DashboardMetrics } from '../components/dashboard/DashboardMetrics';
import { Alert, LoadingSpinner, DataUnavailableNotice } from '../components/common';
import type { ForecastModel } from '../types';

interface OverviewPageProps {
  model: ForecastModel;
}

const OverviewPage: React.FC<OverviewPageProps> = ({ model }) => {
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useForecastSummary(model);
  const { data: cycleInfo, isLoading: cycleLoading } = useLatestCycle(model);
  const { data: health } = useHealth();
  const { data: cached } = useCachedForecasts();
  const downloadMutation = useDownloadForecast();

  const handleDownload = () => {
    downloadMutation.mutate({ model });
  };

  const isLoading = summaryLoading || cycleLoading;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">RainCast AI — Overview</h1>
          <p className="text-sm text-slate-400 mt-1">
            ECMWF {model.toUpperCase()} rainfall forecasting for India
          </p>
        </div>
        <button
          onClick={handleDownload}
          disabled={downloadMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {downloadMutation.isPending ? (
            <RefreshCw size={16} className="animate-spin" />
          ) : (
            <Download size={16} />
          )}
          {downloadMutation.isPending ? 'Downloading...' : 'Fetch Latest'}
        </button>
      </div>

      {/* Download status */}
      {downloadMutation.isSuccess && (
        <Alert
          type="success"
          title="Forecast Downloaded"
          message={`${model.toUpperCase()} forecast data retrieved successfully.`}
        />
      )}
      {downloadMutation.isError && (
        <Alert
          type="error"
          title="Download Failed"
          message={`Could not fetch ${model.toUpperCase()} data: ${downloadMutation.error?.message}. ECMWF data requires internet access.`}
        />
      )}

      {/* ECMWF status banner */}
      {health && !health.ecmwf_accessible && (
        <Alert
          type="warning"
          title="ECMWF Server Not Accessible"
          message="The ECMWF data server is not reachable from this environment. Live forecast data cannot be downloaded. This application requires network access to data.ecmwf.int to retrieve actual forecast files."
        />
      )}

      {/* Key metrics */}
      <section>
        <h2 className="section-title mb-3 flex items-center gap-2">
          <Activity size={18} className="text-sky-400" />
          Forecast Dashboard
        </h2>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner label="Loading forecast summary..." />
          </div>
        ) : (
          <DashboardMetrics
            summary={summary}
            model={model}
            loading={isLoading}
          />
        )}
      </section>

      {/* Model info cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Latest Cycle */}
        <div className="card">
          <h3 className="section-title mb-3 flex items-center gap-2">
            <CloudRain size={18} className="text-sky-400" />
            Latest Forecast Run
          </h3>
          {cycleInfo ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-navy-700">
                <span className="text-slate-400 text-sm">Model</span>
                <span className="text-white font-semibold">{cycleInfo.model}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-navy-700">
                <span className="text-slate-400 text-sm">Init Date</span>
                <span className="text-white font-mono text-sm">{cycleInfo.latest_date}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-navy-700">
                <span className="text-slate-400 text-sm">Init Cycle</span>
                <span className="text-white font-mono text-sm">{String(cycleInfo.latest_cycle).padStart(2, '0')}:00 UTC</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-slate-400 text-sm">ECMWF Server</span>
                <span className={`text-sm font-medium ${cycleInfo.ecmwf_accessible ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {cycleInfo.ecmwf_accessible ? '✓ Accessible' : '✗ Not accessible'}
                </span>
              </div>
            </div>
          ) : (
            <LoadingSpinner size="sm" />
          )}
        </div>

        {/* Cached data */}
        <div className="card">
          <h3 className="section-title mb-3 flex items-center gap-2">
            <Layers size={18} className="text-sky-400" />
            Cached Forecasts
          </h3>
          {cached ? (
            <div className="space-y-2">
              <p className="text-2xl font-bold text-white">{cached.count}</p>
              <p className="text-sm text-slate-400">locally cached forecast files</p>
              {cached.forecasts.slice(0, 3).map((f: any, i: number) => (
                <div key={i} className="flex items-center gap-2 py-1 border-t border-navy-700">
                  <span className="badge badge-blue text-xs">{f.model?.toUpperCase()}</span>
                  <span className="text-xs text-slate-400 font-mono">
                    {f.init_date} /{f.init_cycle?.toString().padStart(2, '0')}Z
                  </span>
                  <span className="text-xs text-slate-500 ml-auto">
                    {f.file_size_bytes ? `${(f.file_size_bytes / 1e6).toFixed(1)} MB` : ''}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <LoadingSpinner size="sm" />
          )}
        </div>
      </div>

      {/* How it works */}
      <div className="card">
        <h3 className="section-title mb-3 flex items-center gap-2">
          <TrendingUp size={18} className="text-sky-400" />
          How RainCast AI Works
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            {
              step: '1',
              title: 'Data Retrieval',
              desc: 'Downloads genuine ECMWF open data GRIB2 files from data.ecmwf.int using the official ecmwf-opendata client.',
            },
            {
              step: '2',
              title: 'GRIB2 Processing',
              desc: 'Parses meteorological GRIB2 files using cfgrib/xarray. Extracts grid coordinates, units, and forecast steps.',
            },
            {
              step: '3',
              title: 'Precipitation Conversion',
              desc: 'Converts ECMWF cumulative precipitation (metres) to incremental mm per step. Incremental = Acc[n] - Acc[n-1].',
            },
            {
              step: '4',
              title: 'Spatial Analysis',
              desc: 'Subsets the global grid to India\'s bounding box. Extracts point forecasts for specific locations.',
            },
          ].map((s) => (
            <div key={s.step} className="bg-navy-800 rounded-lg p-4">
              <div className="w-7 h-7 bg-sky-600 rounded-full flex items-center justify-center text-white text-xs font-bold mb-2">
                {s.step}
              </div>
              <p className="text-sm font-semibold text-white mb-1">{s.title}</p>
              <p className="text-xs text-slate-400">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
