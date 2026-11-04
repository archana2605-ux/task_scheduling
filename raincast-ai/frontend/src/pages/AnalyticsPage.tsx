import React from 'react';
import { BarChart3, Layers } from 'lucide-react';
import { useRainfallCategories, useIndiaRegions } from '../api/hooks';
import { LoadingSpinner } from '../components/common';

const AnalyticsPage: React.FC = () => {
  const { data: categoriesData } = useRainfallCategories();
  const { data: regionsData } = useIndiaRegions();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 size={22} className="text-sky-400" />
          Rainfall Analytics
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          IMD classification thresholds, regional definitions, and analytical reference data
        </p>
      </div>

      {/* IMD Rainfall categories */}
      <div className="card">
        <h3 className="section-title mb-1 flex items-center gap-2">
          <Layers size={16} className="text-sky-400" />
          IMD Rainfall Intensity Categories
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Source: India Meteorological Department. These are display classification thresholds — not official weather warnings.
        </p>
        {categoriesData ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700">
                  {['Category', 'Min (mm)', 'Max (mm)', 'Colour'].map((h) => (
                    <th key={h} className="text-left py-2 px-3 text-slate-400 text-xs font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {categoriesData.categories.map((cat, i) => (
                  <tr key={cat.label} className={`border-b border-navy-800 ${i % 2 === 0 ? 'bg-navy-900/30' : ''}`}>
                    <td className="py-2 px-3 text-white font-medium">{cat.label}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono">{cat.min_mm}</td>
                    <td className="py-2 px-3 text-slate-300 font-mono">{cat.max_mm ?? '∞'}</td>
                    <td className="py-2 px-3">
                      <span
                        className="inline-block w-6 h-4 rounded border border-navy-600"
                        style={{ backgroundColor: cat.color }}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <LoadingSpinner size="sm" />
        )}
      </div>

      {/* India meteorological regions */}
      <div className="card">
        <h3 className="section-title mb-4">India Meteorological Sub-Regions</h3>
        {regionsData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {regionsData.regions.map((region) => (
              <div key={region.name} className="bg-navy-800 rounded-lg p-4 border-l-4" style={{ borderColor: region.color }}>
                <h4 className="font-semibold text-white mb-2">{region.name}</h4>
                <p className="text-xs text-slate-400 mb-2">
                  {region.states.join(' • ')}
                </p>
                <div className="grid grid-cols-2 gap-1 text-xs text-slate-500 font-mono">
                  <span>Lat: {region.bbox.lat_min}°–{region.bbox.lat_max}°N</span>
                  <span>Lon: {region.bbox.lon_min}°–{region.bbox.lon_max}°E</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <LoadingSpinner size="sm" />
        )}
      </div>

      {/* Precipitation data notes */}
      <div className="card">
        <h3 className="section-title mb-4">Technical Notes — Precipitation Accumulation</h3>
        <div className="prose prose-sm prose-invert max-w-none space-y-3 text-slate-300 text-sm">
          <p>
            <strong className="text-white">ECMWF Total Precipitation (tp)</strong> is a cumulative field.
            Each forecast step stores the total rain accumulated from the model initialisation time, not rain
            during that individual period.
          </p>
          <p>
            <strong className="text-white">Incremental conversion:</strong> To obtain rainfall for a specific
            period, RainCast AI subtracts consecutive accumulated values:
          </p>
          <code className="block bg-navy-950 rounded px-4 py-2 font-mono text-sky-300 text-xs">
            incremental[n] = accumulated[n] - accumulated[n-1]
            {'\n'}
            incremental[0] = accumulated[0]  # always ≈ 0 at step 0
          </code>
          <p>
            <strong className="text-white">Units:</strong> ECMWF delivers tp in metres of water equivalent.
            RainCast AI multiplies by 1000 to convert to millimetres for display. Units are verified from
            GRIB2 metadata rather than assumed.
          </p>
          <p>
            <strong className="text-white">Negative differences:</strong> Very small negative values (&lt; 0.01 mm)
            caused by floating-point rounding are clamped to zero. Larger negatives are flagged as anomalies
            and not silently converted to zero.
          </p>
          <p>
            <strong className="text-white">Step availability:</strong> ECMWF IFS 00/12 UTC runs provide steps
            to +240h. 06/18 UTC runs provide steps to +144h. AIFS provides steps to +360h. Only actually
            available steps are requested.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
