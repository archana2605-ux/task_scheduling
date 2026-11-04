import React from 'react';
import { CloudRain, AlertCircle, CheckCircle, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { useHealth, useLatestCycle } from '../../api/hooks';
import type { ForecastModel } from '../../types';

interface HeaderProps {
  model: ForecastModel;
}

export const Header: React.FC<HeaderProps> = ({ model }) => {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: cycleInfo } = useLatestCycle(model);

  const ecmwfOk = health?.ecmwf_accessible;
  const initTime = cycleInfo?.init_datetime
    ? new Date(cycleInfo.init_datetime).toUTCString().replace(' GMT', ' UTC')
    : '—';

  return (
    <header className="sticky top-0 z-10 bg-navy-950/90 backdrop-blur border-b border-navy-800 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Forecast info */}
        <div className="flex items-center gap-4">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wide">Model Run</p>
            <p className="text-sm font-medium text-white font-mono">
              {model.toUpperCase()} / {initTime}
            </p>
          </div>
        </div>

        {/* Right: Status indicators */}
        <div className="flex items-center gap-4">
          {/* ECMWF status */}
          <div className="flex items-center gap-2">
            {healthLoading ? (
              <RefreshCw size={14} className="text-slate-400 animate-spin" />
            ) : ecmwfOk ? (
              <Wifi size={14} className="text-emerald-400" />
            ) : (
              <WifiOff size={14} className="text-amber-400" />
            )}
            <span className={`text-xs font-medium ${ecmwfOk ? 'text-emerald-400' : 'text-amber-400'}`}>
              ECMWF {ecmwfOk ? 'Online' : 'Offline'}
            </span>
          </div>

          {/* Cache indicator */}
          {health && (
            <div className="flex items-center gap-1.5">
              <Database size={14} className="text-slate-400" />
              <span className="text-xs text-slate-400">
                {health.cache_entries} cached
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

function Database({ size, className }: { size: number; className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  );
}
