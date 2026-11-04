import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import type { PrecipitationStep, RainfallForecast } from '../../types';
import { classifyRainfall, getRainfallColor } from '../../types';

// ─── Custom Tooltip ───────────────────────────────────────────────────────────

const RainTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-800 border border-navy-600 rounded-lg p-3 shadow-xl text-xs">
      <p className="text-slate-400 mb-1 font-medium">Step +{label}h</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-semibold">
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value} mm
        </p>
      ))}
    </div>
  );
};

// ─── Hourly Rainfall Bar Chart ────────────────────────────────────────────────

interface HourlyRainfallChartProps {
  steps: PrecipitationStep[];
  title?: string;
}

export const HourlyRainfallChart: React.FC<HourlyRainfallChartProps> = ({ steps, title }) => {
  const data = steps.map((s) => ({
    step: s.step_hours,
    incremental: parseFloat(s.incremental_mm.toFixed(2)),
    accumulated: parseFloat(s.accumulated_mm.toFixed(2)),
    color: getRainfallColor(s.incremental_mm),
  }));

  return (
    <div className="card">
      <h3 className="section-title mb-4">{title || 'Hourly Rainfall Forecast'}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b35ae33" />
          <XAxis
            dataKey="step"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            tickFormatter={(v) => `+${v}h`}
            label={{ value: 'Lead time (hours)', position: 'insideBottom', fill: '#64748b', fontSize: 11, dy: 10 }}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            label={{ value: 'mm', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
          />
          <Tooltip content={<RainTooltip />} />
          <Bar dataKey="incremental" name="Incremental rain" radius={[2, 2, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-500 mt-2 text-center">
        Incremental precipitation per forecast step — not cumulative totals
      </p>
    </div>
  );
};

// ─── Accumulated Rainfall Line Chart ─────────────────────────────────────────

export const AccumulatedRainfallChart: React.FC<{ steps: PrecipitationStep[] }> = ({ steps }) => {
  const data = steps.map((s) => ({
    step: s.step_hours,
    accumulated: parseFloat(s.accumulated_mm.toFixed(2)),
    incremental: parseFloat(s.incremental_mm.toFixed(2)),
  }));

  return (
    <div className="card">
      <h3 className="section-title mb-4">Accumulated Rainfall</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="accGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b35ae33" />
          <XAxis dataKey="step" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `+${v}h`} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Tooltip content={<RainTooltip />} />
          <Area
            type="monotone"
            dataKey="accumulated"
            name="Accumulated"
            stroke="#38bdf8"
            fill="url(#accGrad)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// ─── Model Comparison Chart ───────────────────────────────────────────────────

interface ModelComparisonChartProps {
  ifsSteps?: PrecipitationStep[];
  aifsSteps?: PrecipitationStep[];
}

export const ModelComparisonChart: React.FC<ModelComparisonChartProps> = ({ ifsSteps, aifsSteps }) => {
  // Align steps by step_hours
  const ifsMap = new Map(ifsSteps?.map((s) => [s.step_hours, s.incremental_mm]) ?? []);
  const aifsMap = new Map(aifsSteps?.map((s) => [s.step_hours, s.incremental_mm]) ?? []);
  const allSteps = [...new Set([...ifsMap.keys(), ...aifsMap.keys()])].sort((a, b) => a - b);

  const data = allSteps.map((step) => ({
    step,
    IFS: ifsMap.has(step) ? parseFloat(ifsMap.get(step)!.toFixed(2)) : null,
    AIFS: aifsMap.has(step) ? parseFloat(aifsMap.get(step)!.toFixed(2)) : null,
    diff:
      ifsMap.has(step) && aifsMap.has(step)
        ? parseFloat((ifsMap.get(step)! - aifsMap.get(step)!).toFixed(2))
        : null,
  }));

  return (
    <div className="card">
      <h3 className="section-title mb-4">IFS vs AIFS Comparison</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b35ae33" />
          <XAxis dataKey="step" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `+${v}h`} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Tooltip content={<RainTooltip />} />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
          {ifsSteps && (
            <Line type="monotone" dataKey="IFS" stroke="#38bdf8" strokeWidth={2} dot={false} />
          )}
          {aifsSteps && (
            <Line type="monotone" dataKey="AIFS" stroke="#a78bfa" strokeWidth={2} dot={false} strokeDasharray="5 3" />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// ─── Rainfall Distribution Chart ─────────────────────────────────────────────

export const RainfallDistributionChart: React.FC<{ steps: PrecipitationStep[] }> = ({ steps }) => {
  const categories = [
    { name: 'No rain', min: 0, max: 0, color: '#64748b' },
    { name: 'Very light', min: 0.001, max: 2.5, color: '#bae6fd' },
    { name: 'Light', min: 2.5, max: 15, color: '#38bdf8' },
    { name: 'Moderate', min: 15, max: 64.5, color: '#0284c7' },
    { name: 'Heavy', min: 64.5, max: 115.5, color: '#1e40af' },
    { name: 'Very heavy', min: 115.5, max: 204.5, color: '#7e22ce' },
    { name: 'Extreme', min: 204.5, max: Infinity, color: '#be123c' },
  ];

  const data = categories.map((cat) => ({
    name: cat.name,
    count: steps.filter((s) => s.incremental_mm >= cat.min && s.incremental_mm < cat.max).length,
    color: cat.color,
  }));

  return (
    <div className="card">
      <h3 className="section-title mb-1">Rainfall Intensity Distribution</h3>
      <p className="text-xs text-slate-500 mb-4">IMD categories (display only, not official warnings)</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b35ae33" />
          <XAxis
            dataKey="name"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            angle={-30}
            textAnchor="end"
          />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Tooltip
            formatter={(val: number) => [`${val} steps`, 'Count']}
            contentStyle={{ background: '#1e2470', border: '1px solid #2b35ae', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Bar dataKey="count" radius={[2, 2, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ─── 24/48/72h Summary Bars ───────────────────────────────────────────────────

export const PeriodSummaryChart: React.FC<{ forecast: RainfallForecast }> = ({ forecast }) => {
  const data = [
    { period: '24h', mm: parseFloat(forecast.total_24h_mm.toFixed(2)) },
    { period: '48h', mm: parseFloat(forecast.total_48h_mm.toFixed(2)) },
    { period: '72h', mm: parseFloat(forecast.total_72h_mm.toFixed(2)) },
  ];

  return (
    <div className="card">
      <h3 className="section-title mb-4">Accumulated Rainfall by Period</h3>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b35ae33" />
          <XAxis dataKey="period" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} unit=" mm" />
          <Tooltip
            formatter={(val: number) => [`${val.toFixed(2)} mm`, 'Total rain']}
            contentStyle={{ background: '#1e2470', border: '1px solid #2b35ae', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Bar dataKey="mm" name="Total rain" fill="#38bdf8" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={getRainfallColor(entry.mm / (i + 1))} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
