import React from 'react';
import { CloudRain, Droplets, TrendingUp, AlertTriangle, Clock, Zap, Grid3X3 } from 'lucide-react';
import { MetricCard } from '../common';
import type { ForecastSummary, RainfallForecast } from '../../types';
import { classifyRainfall } from '../../types';

interface DashboardMetricsProps {
  summary?: ForecastSummary;
  forecast?: RainfallForecast;
  model: string;
  loading?: boolean;
}

export const DashboardMetrics: React.FC<DashboardMetricsProps> = ({
  summary,
  forecast,
  model,
  loading,
}) => {
  const initTime = forecast?.metadata.init_datetime
    ? new Date(forecast.metadata.init_datetime).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        dateStyle: 'short',
        timeStyle: 'short',
      })
    : '—';

  const retrievedAt = forecast?.metadata.retrieved_at
    ? new Date(forecast.metadata.retrieved_at).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        timeStyle: 'short',
      })
    : '—';

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <MetricCard
        label="Selected Model"
        value={model.toUpperCase()}
        icon={<Zap size={16} />}
        color="text-sky-300"
        loading={loading}
      />
      <MetricCard
        label="Init Time (IST)"
        value={initTime}
        icon={<Clock size={16} />}
        color="text-slate-200"
        loading={loading}
      />
      <MetricCard
        label="Forecast +24h"
        value={forecast ? forecast.total_24h_mm.toFixed(1) : '—'}
        unit="mm"
        icon={<CloudRain size={16} />}
        color="text-sky-300"
        loading={loading}
      />
      <MetricCard
        label="Forecast +72h"
        value={forecast ? forecast.total_72h_mm.toFixed(1) : '—'}
        unit="mm"
        icon={<CloudRain size={16} />}
        color="text-blue-300"
        loading={loading}
      />
      <MetricCard
        label="Max Step Rain"
        value={forecast ? forecast.max_step_mm.toFixed(1) : '—'}
        unit="mm"
        icon={<AlertTriangle size={16} />}
        color="text-amber-300"
        loading={loading}
      />
      <MetricCard
        label="Intensity"
        value={forecast ? classifyRainfall(forecast.max_step_mm) : '—'}
        icon={<Droplets size={16} />}
        color="text-purple-300"
        loading={loading}
      />
      <MetricCard
        label="Mean Step Rain"
        value={forecast ? forecast.mean_mm.toFixed(2) : '—'}
        unit="mm"
        icon={<TrendingUp size={16} />}
        color="text-emerald-300"
        loading={loading}
      />
      <MetricCard
        label="Data Updated"
        value={retrievedAt}
        icon={<Grid3X3 size={16} />}
        color="text-slate-300"
        loading={loading}
      />
    </div>
  );
};
