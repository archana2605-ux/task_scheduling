import React, { useState, useRef, useEffect } from 'react';
import { Search, MapPin, X, Loader } from 'lucide-react';
import { useLocationSearch } from '../../api/hooks';
import type { LocationResult } from '../../types';

interface LocationSearchProps {
  onSelect: (location: LocationResult) => void;
  selectedLocation?: LocationResult | null;
}

export const LocationSearch: React.FC<LocationSearchProps> = ({ onSelect, selectedLocation }) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: results, isLoading } = useLocationSearch(query);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (loc: LocationResult) => {
    onSelect(loc);
    setQuery('');
    setIsOpen(false);
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className="relative w-full">
      {/* Input */}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setIsOpen(true); }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search city, district, state..."
          className="w-full bg-navy-800 border border-navy-600 rounded-lg pl-9 pr-9 py-2.5 text-sm text-white
                     placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
        />
        {(query || isLoading) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {isLoading ? (
              <Loader size={14} className="text-slate-400 animate-spin" />
            ) : (
              <button onClick={handleClear}>
                <X size={14} className="text-slate-400 hover:text-white" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Selected location display */}
      {selectedLocation && !query && (
        <div className="mt-2 flex items-center gap-2 bg-sky-900/30 border border-sky-700/50 rounded-lg px-3 py-2">
          <MapPin size={14} className="text-sky-400 shrink-0" />
          <div className="min-w-0">
            <p className="text-sm font-medium text-white truncate">{selectedLocation.name}</p>
            <p className="text-xs text-slate-400 truncate">{selectedLocation.state}</p>
          </div>
          <span className="text-xs text-slate-500 ml-auto font-mono">
            {selectedLocation.lat.toFixed(2)}°N {selectedLocation.lon.toFixed(2)}°E
          </span>
        </div>
      )}

      {/* Dropdown results */}
      {isOpen && query.length >= 2 && (
        <div className="absolute top-full mt-1 w-full bg-navy-800 border border-navy-600 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto">
          {results && results.length > 0 ? (
            results.map((loc, i) => (
              <button
                key={`${loc.name}-${i}`}
                onClick={() => handleSelect(loc)}
                className="w-full flex items-start gap-3 px-4 py-3 hover:bg-navy-700 transition-colors text-left"
              >
                <MapPin size={14} className="text-slate-400 shrink-0 mt-0.5" />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-white">{loc.name}</p>
                  <p className="text-xs text-slate-400">
                    {loc.district}, {loc.state}
                  </p>
                </div>
                <span className="text-xs text-slate-500 ml-auto font-mono shrink-0">
                  {loc.lat.toFixed(2)}°N
                </span>
              </button>
            ))
          ) : (
            <div className="px-4 py-3 text-sm text-slate-400 text-center">
              {isLoading ? 'Searching...' : 'No locations found'}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
