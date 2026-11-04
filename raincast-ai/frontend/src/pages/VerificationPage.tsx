import React from 'react';
import { Activity } from 'lucide-react';
import { Alert } from '../components/common';

const VerificationPage: React.FC = () => (
  <div className="p-6 space-y-6 max-w-7xl mx-auto">
    <div>
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Activity size={22} className="text-sky-400" />
        Forecast Verification
      </h1>
      <p className="text-sm text-slate-400 mt-1">
        Statistical evaluation of forecast accuracy against observed rainfall
      </p>
    </div>

    <Alert
      type="info"
      title="Verification Data Required"
      message="Forecast verification requires observed rainfall data (e.g., rain gauge networks, radar composites, or satellite-derived estimates). This module displays verification scores when observation data is provided. Currently, no observation data source is connected. Future integration: IMD station data, IMDAA reanalysis, or GPM IMERG satellite precipitation."
    />

    <div className="card">
      <h3 className="section-title mb-4">Planned Verification Metrics</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {[
          { label: 'RMSE', desc: 'Root Mean Square Error between forecast and observed mm values' },
          { label: 'Bias', desc: 'Systematic over- or under-prediction in mm' },
          { label: 'Correlation', desc: 'Pearson correlation of spatial rainfall patterns' },
          { label: 'POD', desc: 'Probability of Detection for rain/no-rain events' },
          { label: 'FAR', desc: 'False Alarm Rate for heavy rainfall events' },
          { label: 'ETS', desc: 'Equitable Threat Score for threshold exceedance' },
        ].map((m) => (
          <div key={m.label} className="bg-navy-800 rounded-lg p-4">
            <p className="font-mono font-bold text-sky-300 mb-1">{m.label}</p>
            <p className="text-xs text-slate-400">{m.desc}</p>
          </div>
        ))}
      </div>
    </div>

    <div className="card">
      <h3 className="section-title mb-3">How to Connect Observation Data</h3>
      <div className="bg-navy-950 rounded-lg p-4 font-mono text-xs text-sky-300 space-y-1">
        <p># Add observation data endpoint to backend config</p>
        <p>OBSERVATION_SOURCE=imd_gridded   # or gpm_imerg / rain_gauge</p>
        <p>OBSERVATION_API_URL=https://your-obs-api.example.com</p>
      </div>
      <p className="text-xs text-slate-400 mt-3">
        Once an observation source is configured, this page will display verification scores,
        lead-time dependent skill, and regional accuracy breakdowns comparing IFS and AIFS.
      </p>
    </div>
  </div>
);

export default VerificationPage;
