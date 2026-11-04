import React from 'react';
import { Database, ExternalLink, FileCode, Cloud } from 'lucide-react';

const DataSourcesPage: React.FC = () => (
  <div className="p-6 space-y-6 max-w-7xl mx-auto">
    <div>
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Database size={22} className="text-sky-400" />
        Data Sources
      </h1>
      <p className="text-sm text-slate-400 mt-1">
        All forecast data comes from official ECMWF open data sources
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* ECMWF Open Data */}
      <div className="card border-t-2 border-sky-500">
        <h3 className="section-title mb-3 flex items-center gap-2">
          <Cloud size={18} className="text-sky-400" />
          ECMWF Open Data
        </h3>
        <div className="space-y-3 text-sm text-slate-300">
          <p>Primary data source for all forecast products.</p>
          <div className="space-y-2">
            {[
              { label: 'Provider', value: 'European Centre for Medium-Range Weather Forecasts (ECMWF)' },
              { label: 'Access method', value: 'Official ecmwf-opendata Python client' },
              { label: 'Data server', value: 'data.ecmwf.int' },
              { label: 'File format', value: 'GRIB2 (WMO standard)' },
              { label: 'Licence', value: 'CC-BY 4.0' },
              { label: 'Update frequency', value: '4× daily (00, 06, 12, 18 UTC)' },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between py-1 border-b border-navy-700">
                <span className="text-slate-400">{label}</span>
                <span className="text-white text-right max-w-xs">{value}</span>
              </div>
            ))}
          </div>
          <div className="pt-2 space-y-1">
            <a
              href="https://www.ecmwf.int/en/forecasts/datasets/open-data"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sky-400 hover:text-sky-300 text-xs"
            >
              <ExternalLink size={12} />
              ECMWF Open Data documentation
            </a>
            <a
              href="https://github.com/ecmwf/ecmwf-opendata"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sky-400 hover:text-sky-300 text-xs"
            >
              <ExternalLink size={12} />
              ecmwf-opendata GitHub
            </a>
          </div>
        </div>
      </div>

      {/* IFS */}
      <div className="card border-t-2 border-blue-500">
        <h3 className="section-title mb-3">IFS — Integrated Forecasting System</h3>
        <div className="space-y-2 text-sm">
          {[
            { label: 'Model type', value: 'Physics-based NWP (Numerical Weather Prediction)' },
            { label: 'Resolution (open data)', value: '0.25° global' },
            { label: 'Forecast range', value: '0–240h (00/12Z), 0–144h (06/18Z)' },
            { label: 'Step interval', value: '3h (0–144h), 6h (144–240h)' },
            { label: 'Key parameters', value: 'tp, 2t, sp, tcc, 10u, 10v' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between py-1 border-b border-navy-700">
              <span className="text-slate-400 shrink-0">{label}</span>
              <span className="text-white text-right">{value}</span>
            </div>
          ))}
          <p className="text-xs text-slate-500 pt-2 italic">
            Gold standard for medium-range weather forecasting. Uses spectral atmospheric model.
          </p>
        </div>
      </div>

      {/* AIFS */}
      <div className="card border-t-2 border-purple-500">
        <h3 className="section-title mb-3">AIFS — AI/Integrated Forecasting System</h3>
        <div className="space-y-2 text-sm">
          {[
            { label: 'Model type', value: 'Machine Learning (data-driven)' },
            { label: 'Resolution (open data)', value: '0.25° global' },
            { label: 'Forecast range', value: '0–360h' },
            { label: 'Step interval', value: '6h' },
            { label: 'Training data', value: 'ERA5 reanalysis + IFS analysis' },
            { label: 'Key parameters', value: 'tp, 2t, 10u, 10v, msl' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between py-1 border-b border-navy-700">
              <span className="text-slate-400 shrink-0">{label}</span>
              <span className="text-white text-right">{value}</span>
            </div>
          ))}
          <p className="text-xs text-slate-500 pt-2 italic">
            ML-based alternative. Orders of magnitude faster than IFS. Uses IFS for initial conditions.
          </p>
        </div>
      </div>

      {/* Processing stack */}
      <div className="card border-t-2 border-emerald-500">
        <h3 className="section-title mb-3 flex items-center gap-2">
          <FileCode size={16} className="text-emerald-400" />
          Processing Stack
        </h3>
        <div className="space-y-2 text-sm">
          {[
            { label: 'GRIB2 reading', value: 'cfgrib + ecCodes' },
            { label: 'Array processing', value: 'NumPy + Xarray' },
            { label: 'API backend', value: 'FastAPI + Pydantic' },
            { label: 'Database', value: 'SQLite (dev) / PostgreSQL (prod)' },
            { label: 'Frontend', value: 'React + Vite + TypeScript' },
            { label: 'Maps', value: 'Leaflet + React-Leaflet' },
            { label: 'Charts', value: 'Recharts' },
            { label: 'State management', value: 'TanStack Query' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between py-1 border-b border-navy-700">
              <span className="text-slate-400">{label}</span>
              <span className="text-white text-sm font-mono">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

export default DataSourcesPage;
