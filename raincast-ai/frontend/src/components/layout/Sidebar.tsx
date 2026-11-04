import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  CloudRain, Map, BarChart3, GitCompare, Database,
  Info, Home, TrendingUp, Search, ChevronLeft, ChevronRight,
  Activity, Layers
} from 'lucide-react';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/', label: 'Overview', icon: <Home size={18} /> },
  { path: '/forecast', label: 'Live Forecast', icon: <CloudRain size={18} /> },
  { path: '/map', label: 'Interactive Map', icon: <Map size={18} /> },
  { path: '/location', label: 'Location Forecast', icon: <Search size={18} /> },
  { path: '/comparison', label: 'Model Comparison', icon: <GitCompare size={18} /> },
  { path: '/analytics', label: 'Rainfall Analytics', icon: <BarChart3 size={18} /> },
  { path: '/verification', label: 'Forecast Verification', icon: <Activity size={18} /> },
  { path: '/data-sources', label: 'Data Sources', icon: <Database size={18} /> },
  { path: '/about', label: 'About Research', icon: <Info size={18} /> },
];

interface SidebarProps {
  model: 'ifs' | 'aifs';
  onModelChange: (m: 'ifs' | 'aifs') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ model, onModelChange }) => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={`flex flex-col bg-navy-900 border-r border-navy-700 h-screen sticky top-0 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-navy-700">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <CloudRain size={22} className="text-sky-400" />
            <span className="font-bold text-white text-lg">RainCast AI</span>
          </div>
        )}
        {collapsed && <CloudRain size={22} className="text-sky-400 mx-auto" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-navy-800 text-slate-400 hover:text-white transition-colors ml-auto"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Model Selector */}
      {!collapsed && (
        <div className="p-4 border-b border-navy-700">
          <p className="metric-label mb-2">Forecast Model</p>
          <div className="flex gap-1 bg-navy-950 rounded-lg p-1">
            {(['ifs', 'aifs'] as const).map((m) => (
              <button
                key={m}
                onClick={() => onModelChange(m)}
                className={`flex-1 py-1.5 px-2 rounded text-xs font-semibold transition-all ${
                  model === m
                    ? 'bg-sky-600 text-white shadow'
                    : 'text-slate-400 hover:text-white hover:bg-navy-800'
                }`}
              >
                {m.toUpperCase()}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-1 text-center">
            {model === 'ifs' ? 'ECMWF IFS (NWP)' : 'ECMWF AIFS (ML)'}
          </p>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-sky-900/40 text-sky-300 border border-sky-800/50'
                  : 'text-slate-400 hover:text-white hover:bg-navy-800'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <span className="shrink-0">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-navy-700">
          <p className="text-xs text-slate-500 text-center">
            Data: ECMWF Open Data
          </p>
          <p className="text-xs text-slate-600 text-center">v1.0.0</p>
        </div>
      )}
    </aside>
  );
};
