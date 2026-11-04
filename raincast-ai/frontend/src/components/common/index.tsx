import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';

// ─── Loading Spinner ──────────────────────────────────────────────────────────

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; label?: string }> = ({
  size = 'md',
  label,
}) => {
  const sizeClasses = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <svg
        className={`animate-spin text-sky-400 ${sizeClasses[size]}`}
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {label && <p className="text-sm text-slate-400">{label}</p>}
    </div>
  );
};

// ─── Error Alert ──────────────────────────────────────────────────────────────

interface AlertProps {
  type: 'error' | 'warning' | 'info' | 'success';
  title?: string;
  message: string;
  onDismiss?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, title, message, onDismiss }) => {
  const styles = {
    error: {
      wrapper: 'bg-red-950/50 border-red-800 text-red-200',
      icon: <AlertCircle size={16} className="text-red-400 shrink-0" />,
    },
    warning: {
      wrapper: 'bg-amber-950/50 border-amber-800 text-amber-200',
      icon: <AlertTriangle size={16} className="text-amber-400 shrink-0" />,
    },
    info: {
      wrapper: 'bg-sky-950/50 border-sky-800 text-sky-200',
      icon: <Info size={16} className="text-sky-400 shrink-0" />,
    },
    success: {
      wrapper: 'bg-emerald-950/50 border-emerald-800 text-emerald-200',
      icon: <CheckCircle size={16} className="text-emerald-400 shrink-0" />,
    },
  };

  const { wrapper, icon } = styles[type];

  return (
    <div className={`flex items-start gap-3 border rounded-lg p-3 ${wrapper}`}>
      {icon}
      <div className="flex-1 min-w-0">
        {title && <p className="text-sm font-semibold mb-0.5">{title}</p>}
        <p className="text-sm">{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 opacity-70 hover:opacity-100">
          <X size={14} />
        </button>
      )}
    </div>
  );
};

// ─── Empty State ──────────────────────────────────────────────────────────────

export const EmptyState: React.FC<{ icon?: React.ReactNode; title: string; description?: string }> = ({
  icon,
  title,
  description,
}) => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    {icon && <div className="mb-3 text-slate-600">{icon}</div>}
    <p className="text-slate-400 font-medium">{title}</p>
    {description && <p className="text-sm text-slate-500 mt-1 max-w-sm">{description}</p>}
  </div>
);

// ─── Status Badge ──────────────────────────────────────────────────────────────

interface StatusBadgeProps {
  value: boolean | 'loading';
  trueLabel?: string;
  falseLabel?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  value,
  trueLabel = 'Online',
  falseLabel = 'Offline',
}) => {
  if (value === 'loading') {
    return <span className="badge bg-slate-800 text-slate-400">Checking...</span>;
  }
  return value ? (
    <span className="badge badge-green">{trueLabel}</span>
  ) : (
    <span className="badge badge-amber">{falseLabel}</span>
  );
};

// ─── Metric Card ──────────────────────────────────────────────────────────────

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  icon,
  color = 'text-white',
  trend,
  loading,
}) => (
  <div className="metric-card">
    <div className="flex items-center justify-between">
      <p className="metric-label">{label}</p>
      {icon && <span className="text-slate-500">{icon}</span>}
    </div>
    {loading ? (
      <div className="h-8 bg-navy-800 rounded animate-pulse mt-1" />
    ) : (
      <div className="flex items-baseline gap-1 mt-1">
        <span className={`metric-value ${color}`}>{value}</span>
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
    )}
  </div>
);

// ─── Rainfall Intensity Badge ─────────────────────────────────────────────────

const INTENSITY_STYLES: Record<string, string> = {
  'No rainfall': 'bg-slate-800 text-slate-300',
  'Very light': 'bg-sky-900/50 text-sky-300',
  'Light': 'bg-blue-900/50 text-blue-300',
  'Moderate': 'bg-blue-800/50 text-blue-200',
  'Heavy': 'bg-indigo-900/50 text-indigo-300',
  'Very heavy': 'bg-purple-900/50 text-purple-300',
  'Extremely heavy': 'bg-rose-900/50 text-rose-300',
};

export const RainfallIntensityBadge: React.FC<{ intensity: string }> = ({ intensity }) => (
  <span className={`badge ${INTENSITY_STYLES[intensity] || 'bg-slate-800 text-slate-300'}`}>
    {intensity}
  </span>
);

// ─── Data unavailable notice ───────────────────────────────────────────────────

export const DataUnavailableNotice: React.FC<{ model?: string }> = ({ model }) => (
  <Alert
    type="warning"
    title="Forecast Data Not Available"
    message={`Live ECMWF ${model || ''} data could not be retrieved. This may be due to network connectivity or the ECMWF server not yet having published the latest forecast cycle. No synthetic or placeholder data is shown.`}
  />
);
