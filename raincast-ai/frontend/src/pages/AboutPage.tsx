import React from 'react';
import { Info, CloudRain, Code, AlertTriangle } from 'lucide-react';

const AboutPage: React.FC = () => (
  <div className="p-6 space-y-6 max-w-5xl mx-auto">
    <div>
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Info size={22} className="text-sky-400" />
        About RainCast AI
      </h1>
      <p className="text-sm text-slate-400 mt-1">
        Research-oriented ECMWF-based rainfall forecasting platform for India
      </p>
    </div>

    <div className="card border-l-4 border-sky-500">
      <h3 className="section-title mb-3">Research Objective</h3>
      <p className="text-sm text-slate-300 leading-relaxed">
        RainCast AI is a production-quality web platform for retrieving, processing, and visualising
        ECMWF open data rainfall forecasts over India. It is designed to demonstrate how genuine
        numerical weather prediction (IFS) and machine-learning (AIFS) model outputs can be
        processed, converted, and presented in a research-grade interface.
      </p>
    </div>

    <div className="card">
      <h3 className="section-title mb-4 flex items-center gap-2">
        <Code size={16} className="text-sky-400" />
        Key Technical Contributions
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
        {[
          {
            title: 'Real ECMWF Data',
            desc: 'Retrieves genuine GRIB2 forecast files from data.ecmwf.int using the official ecmwf-opendata client. No synthetic or hardcoded values.',
          },
          {
            title: 'Correct Accumulation Handling',
            desc: 'ECMWF total precipitation is cumulative from init time. We correctly derive incremental values via differencing (Acc[n] - Acc[n-1]), with rigorous edge-case handling.',
          },
          {
            title: 'Unit Verification',
            desc: 'Parameter units are read from GRIB2 metadata rather than assumed. Metres of water equivalent are converted to mm (×1000) only after unit verification.',
          },
          {
            title: 'IFS vs AIFS Comparison',
            desc: 'Compares two independent ECMWF forecasting systems — the physics-based IFS and the ML-based AIFS — with mismatch detection and clear scientific notes.',
          },
          {
            title: 'India-Focused Visualisation',
            desc: 'Interactive Leaflet map centred on India with IMD rainfall classification legend. Regional sub-divisions aligned with meteorological practice.',
          },
          {
            title: 'Transparent Data Handling',
            desc: 'Never shows fake or placeholder rainfall values. If data is unavailable, the platform states so clearly rather than inventing values.',
          },
        ].map((item) => (
          <div key={item.title} className="bg-navy-800 rounded-lg p-4">
            <p className="font-semibold text-white mb-1">{item.title}</p>
            <p className="text-xs text-slate-400">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>

    <div className="card border-l-4 border-amber-500">
      <h3 className="section-title mb-3 flex items-center gap-2">
        <AlertTriangle size={16} className="text-amber-400" />
        Important Disclaimers
      </h3>
      <ul className="space-y-2 text-sm text-slate-300">
        {[
          'RainCast AI retrieves and displays ECMWF operational forecasts. It does not train, modify, or claim ownership of IFS or AIFS models.',
          'IMD rainfall intensity categories shown are display thresholds only — not official India Meteorological Department forecasts or warnings.',
          'Forecast data is subject to ECMWF open data terms of use (CC-BY 4.0). Attribution: Contains modified Copernicus Climate Change Service information.',
          'This platform is research-oriented. For official weather warnings, refer to India Meteorological Department (imd.gov.in).',
          'ECMWF open data has a lag of approximately 6–8 hours after the model initialisation time. The latest available cycle may not be the most recent.',
        ].map((d, i) => (
          <li key={i} className="flex gap-2">
            <span className="text-amber-400 shrink-0">•</span>
            <span>{d}</span>
          </li>
        ))}
      </ul>
    </div>

    <div className="card">
      <h3 className="section-title mb-3">Attribution</h3>
      <div className="text-sm text-slate-400 space-y-1">
        <p>• ECMWF Open Data: <a href="https://www.ecmwf.int/en/forecasts/datasets/open-data" className="text-sky-400 hover:underline" target="_blank" rel="noopener noreferrer">ecmwf.int</a></p>
        <p>• Map tiles: © <a href="https://www.openstreetmap.org/copyright" className="text-sky-400 hover:underline" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors</p>
        <p>• IMD Rainfall Categories: India Meteorological Department</p>
        <p>• ecmwf-opendata Python client: ECMWF (Apache 2.0)</p>
      </div>
    </div>
  </div>
);

export default AboutPage;
