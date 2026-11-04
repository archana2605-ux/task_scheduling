// Core TypeScript types for RainCast AI

export type ForecastModel = 'ifs' | 'aifs';
export type ForecastCycle = 0 | 6 | 12 | 18;

export interface ForecastMetadata {
  model: string;
  init_date: string;
  init_cycle: number;
  init_datetime: string;
  resolution_deg: number;
  max_step_hours: number;
  retrieved_at: string;
  parameters: string[];
  source: string;
}

export interface PrecipitationStep {
  step_hours: number;
  valid_time: string;
  accumulated_mm: number;
  incremental_mm: number;
  accumulation_period_h: number;
}

export interface RainfallForecast {
  metadata: ForecastMetadata;
  steps: PrecipitationStep[];
  total_24h_mm: number;
  total_48h_mm: number;
  total_72h_mm: number;
  max_step_mm: number;
  mean_mm: number;
}

export interface ForecastSummary {
  model: string;
  init_datetime: string;
  india_mean_mm: number;
  india_max_mm: number;
  heavy_rain_grid_cells: number;
  total_grid_cells: number;
  retrieved_at: string;
  is_fresh: boolean;
  data_available: boolean;
  error_message?: string;
}

export interface LocationResult {
  name: string;
  state: string;
  district: string;
  lat: number;
  lon: number;
}

export interface LocationForecastResponse {
  location: { latitude: number; longitude: number };
  forecast: RainfallForecast;
  statistics?: Record<string, number>;
}

export interface ModelComparisonResponse {
  ifs?: RainfallForecast;
  aifs?: RainfallForecast;
  comparison_valid: boolean;
  notes: string[];
  max_diff_mm?: number;
  mean_diff_mm?: number;
}

export interface RainfallCategory {
  label: string;
  min_mm: number;
  max_mm: number | null;
  color: string;
}

export interface IndiaRegion {
  name: string;
  states: string[];
  bbox: { lat_min: number; lat_max: number; lon_min: number; lon_max: number };
  color: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  ecmwf_accessible: boolean;
  latest_ifs_run?: string;
  latest_aifs_run?: string;
  cache_entries: number;
}

export interface LatestCycleInfo {
  model: string;
  latest_date: string;
  latest_cycle: number;
  init_datetime: string;
  ecmwf_accessible: boolean;
  checked_at: string;
}

export interface ModelInfo {
  full_name: string;
  type: string;
  developer: string;
  resolution: string;
  cycles: number[];
  max_lead_time_hours: number;
  description: string;
}

// IMD rainfall intensity classification
export type RainfallIntensity =
  | 'No rainfall'
  | 'Very light'
  | 'Light'
  | 'Moderate'
  | 'Heavy'
  | 'Very heavy'
  | 'Extremely heavy';

export const RAINFALL_COLORS: Record<RainfallIntensity, string> = {
  'No rainfall': '#f0f9ff',
  'Very light': '#bae6fd',
  'Light': '#38bdf8',
  'Moderate': '#0284c7',
  'Heavy': '#1e40af',
  'Very heavy': '#7e22ce',
  'Extremely heavy': '#be123c',
};

export function classifyRainfall(mm: number): RainfallIntensity {
  if (mm <= 0) return 'No rainfall';
  if (mm < 2.5) return 'Very light';
  if (mm < 15) return 'Light';
  if (mm < 64.5) return 'Moderate';
  if (mm < 115.5) return 'Heavy';
  if (mm < 204.5) return 'Very heavy';
  return 'Extremely heavy';
}

export function getRainfallColor(mm: number): string {
  return RAINFALL_COLORS[classifyRainfall(mm)];
}
